from typing import TypedDict, Optional, List, Any, Dict
from datetime import datetime, timezone
import json
import random
from langgraph.graph import StateGraph, END
from sqlalchemy import create_engine, select, update
from sqlalchemy.orm import sessionmaker
from langfuse import Langfuse
from core.adapter import GeminiAdapter
from core.memory import SoulMemory
from core.models import Base, Task, UserSoul
from core.notifier import Notifier

class AgentState(TypedDict):
    """The state of the agent within the orchestrator graph."""
    user_input: str
    intent: Optional[str]
    history: List[dict]
    response: Optional[str]
    proposed_actions: Optional[List[Dict[str, Any]]]
    needs_approval: bool
    notify_user: bool

class SoulOrchestrator:
    """Orchestrates natural language intents using a LangGraph state machine with observability."""

    def __init__(self, db_url: str = "sqlite:///notion_soul.db"):
        """Initializes the SoulOrchestrator with tracing and database support."""
        self.adapter = GeminiAdapter()
        self.memory = SoulMemory()
        self.notifier = Notifier()
        self.langfuse = Langfuse()
        
        # Database setup
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        
        self.graph = self._build_graph()

    def _build_graph(self):
        """Constructs the LangGraph state machine."""
        workflow = StateGraph(AgentState)

        # Define nodes
        workflow.add_node("classify", self._node_classify)
        workflow.add_node("handle_task", self._node_handle_task)
        workflow.add_node("handle_memory", self._node_handle_memory)
        workflow.add_node("handle_planner", self._node_handle_planner)
        workflow.add_node("handle_clarify", self._node_handle_clarify)
        workflow.add_node("await_approval", self._node_await_approval)
        workflow.add_node("notify", self._node_notify)

        # Set entry point
        workflow.set_entry_point("classify")

        # Add conditional edges
        workflow.add_conditional_edges(
            "classify",
            self._route_intent,
            {
                "task": "handle_task",
                "memory": "handle_memory",
                "planner": "handle_planner",
                "clarify": "handle_clarify"
            }
        )

        # Edges
        workflow.add_edge("handle_task", "await_approval")
        workflow.add_edge("handle_memory", "notify") 
        workflow.add_edge("handle_planner", "await_approval")
        workflow.add_edge("handle_clarify", END)
        workflow.add_edge("await_approval", END)
        workflow.add_edge("notify", END)

        return workflow.compile()

    async def _node_classify(self, state: AgentState) -> AgentState:
        """Node: Classifies the user's intent."""
        intent = await self.classify_intent(state["user_input"])
        return {**state, "intent": intent}

    def _route_intent(self, state: AgentState) -> str:
        """Conditional Edge: Routes to the appropriate node based on intent."""
        return state["intent"] or "clarify"

    async def _node_handle_task(self, state: AgentState) -> AgentState:
        """Decomposes a task and persists the entire tree to the database."""
        subtasks = await self.adapter.decompose_task(state["user_input"])
        
        # Recursive Persistence
        with self.Session() as session:
            new_parent = Task(
                title=state["user_input"],
                status='todo',
                sync_status='pending'
            )
            session.add(new_parent)
            session.flush() 
            
            for st in subtasks:
                child = Task(
                    title=st.get("title", "Untitled Subtask"),
                    parent_id=new_parent.id,
                    cognitive_load_score=st.get("estimated_cognitive_load", 0.5), # Default to 0.5 if AI misses it
                    duration_minutes=st.get("duration_minutes", 20),
                    slack_minutes=st.get("slack_minutes", 5),
                    status='todo',
                    sync_status='pending'
                )
                session.add(child)
            
            session.commit()

        return {
            **state, 
            "proposed_actions": subtasks, 
            "needs_approval": True,
            "response": f"I've broken down '{state['user_input']}' into {len(subtasks)} atomic steps. Please approve the plan."
        }

    async def _node_handle_memory(self, state: AgentState) -> AgentState:
        """Processes memory-related intents using SoulMemory and persists to UserSoul table."""
        await self.memory.add_fact(state["user_input"])
        
        with self.Session() as session:
            soul_record = UserSoul(
                key=f"fact_{datetime.now(timezone.utc).timestamp()}",
                value=state["user_input"],
                category="preference"
            )
            session.add(soul_record)
            session.commit()

        return {**state, "response": "I've updated your 'Digital Soul' with this information.", "notify_user": True}

    async def _node_handle_planner(self, state: AgentState) -> AgentState:
        """Node: Handles macro planning requests."""
        return {**state, "response": "Planning logic pending Implementation Phase 3."}

    async def _node_handle_clarify(self, state: AgentState) -> AgentState:
        """Node: Requests clarification for ambiguous input."""
        return {**state, "response": "I'm not quite sure what you mean. Could you provide more details?"}

    async def _node_await_approval(self, state: AgentState) -> AgentState:
        """Node: Represents the state where the agent is waiting for user confirmation."""
        return {**state, "response": state.get("response", "Waiting for your approval.")}

    async def _node_notify(self, state: AgentState) -> AgentState:
        """Node: Sends a notification if the state requires it."""
        if state.get("notify_user"):
            await self.notifier.send_bark("Digital Soul Updated", state["response"])
        return state

    async def approve_plan(self, task_title: str):
        """Action: User approves a proposed task tree."""
        with self.Session() as session:
            stmt = update(Task).where(Task.title == task_title).values(sync_status='approved')
            session.execute(stmt)
            parent_stmt = select(Task.id).where(Task.title == task_title)
            parent_id = session.execute(parent_stmt).scalar_one_or_none()
            if parent_id:
                child_stmt = update(Task).where(Task.parent_id == parent_id).values(sync_status='approved')
                session.execute(child_stmt)
            session.commit()

    async def handle_user_response(self, task_id: int, user_feedback: str) -> Dict[str, Any]:
        """Processes user feedback from a nudge and triggers a re-plan if needed."""
        with self.Session() as session:
            stmt = select(Task).where(Task.id == task_id)
            task = session.execute(stmt).scalars().one_or_none()
            
            if not task:
                return {"action": "Error", "message": "Task not found"}
            
            prompt = f"User feedback for task '{task.title}': '{user_feedback}'.\nStatus: {task.status}.\n\nPlease provide a scientific re-plan suggestion."
            
            response_text = await self.adapter.generate_content(prompt, skill_name='proactive-nudger')
            
            clean_json = response_text.strip()
            if "```json" in clean_json:
                clean_json = clean_json.split("```json")[1].split("```")[0].strip()
            
            try:
                data = json.loads(clean_json)
                ai_action = data.get("suggested_action", "Continue")
                if ai_action == "Delay":
                    task.status = 'todo'
                    task.sync_status = 'pending'
                elif ai_action == "Skip":
                    task.status = 'done'
                
                session.commit()
                
                return {
                    "action": ai_action,
                    "response": data.get("nudge_message", "Updated."),
                    "reasoning": data.get("reasoning", "Adaptive adjustment.")
                }
            except Exception:
                return {"action": "Continue", "response": "I've noted your feedback."}

    async def classify_intent(self, user_input: str) -> str:
        """Determines the intent of the user's input with improved prompt."""
        prompt = f"""
        Classify the following user input into EXACTLY one of these categories:
        - 'task': If the user wants to add, create, or do a specific task/project.
        - 'memory': If the user is sharing a preference, habit, or personal fact.
        - 'planner': If the user wants to reschedule the entire week or month.
        - 'clarify': If the input is too vague.

        Input: {user_input}
        Output only the category name (lowercase).
        """
        response = await self.adapter.generate_content(prompt)
        clean_response = response.strip().lower()
        if clean_response in ['task', 'memory', 'planner', 'clarify']:
            return clean_response
        return 'clarify'

    async def evaluate_nudge(self) -> Dict[str, Any]:
        """Heartbeat Logic: Evaluates current active tasks and decides if a nudge is needed."""
        with self.Session() as session:
            stmt = select(Task).where(Task.status == 'in_progress').order_by(Task.updated_at.desc())
            active_task = session.execute(stmt).scalars().first()
            
            if not active_task:
                return {"nudge_needed": False}
            
            prompt = f"Active Task: '{active_task.title}'. Started at: {active_task.created_at}. Expected Duration: {active_task.duration_minutes}m. Slack: {active_task.slack_minutes}m.\n\nPlease decide if a nudge is needed."
            
            response_text = await self.adapter.generate_content(prompt, skill_name='proactive-nudger')
            
            clean_json = response_text.strip()
            if "```json" in clean_json:
                clean_json = clean_json.split("```json")[1].split("```")[0].strip()
            
            try:
                data = json.loads(clean_json)
                return {
                    "nudge_needed": True,
                    "message": data.get("nudge_message", "How is the task going?"),
                    "action": data.get("suggested_action", "Continue"),
                    "task_id": active_task.id
                }
            except Exception:
                return {"nudge_needed": False, "error": "AI response parsing failed"}

    async def get_optimized_view(self) -> Dict[str, Any]:
        """Fetches tasks and returns a scientifically interleaved view for the dashboard."""
        with self.Session() as session:
            stmt = select(Task)
            all_tasks = session.execute(stmt).scalars().all()
            
            # Filter for viewable tasks (no parent or approved)
            viewable_tasks = [t for t in all_tasks if t.parent_id is None or t.sync_status == 'approved']
            
            # SOTA Interleaving Logic: 
            # 1. Fill scores if missing (randomize for variety if not set)
            for t in viewable_tasks:
                if t.cognitive_load_score == 0.0:
                    t.cognitive_load_score = round(random.uniform(0.1, 0.9), 2)
            
            heavy_tasks = [t for t in viewable_tasks if t.cognitive_load_score >= 0.5]
            light_tasks = [t for t in viewable_tasks if t.cognitive_load_score < 0.5]
            
            heavy_tasks.sort(key=lambda x: x.cognitive_load_score, reverse=True)
            light_tasks.sort(key=lambda x: x.cognitive_load_score, reverse=True)
            
            interleaved = []
            while heavy_tasks or light_tasks:
                if heavy_tasks:
                    interleaved.append(heavy_tasks.pop(0))
                if light_tasks:
                    interleaved.append(light_tasks.pop(0))
            
            calendar_view = []
            for i, t in enumerate(interleaved):
                hour = 9 + i
                calendar_view.append({
                    "id": t.id,
                    "time": f"{hour:02d}:00",
                    "title": t.title,
                    "load": t.cognitive_load_score,
                    "duration": t.duration_minutes,
                    "slack": t.slack_minutes
                })
                
            return {
                "calendar": calendar_view,
                "kanban": {
                    "todo": [t.title for t in viewable_tasks if t.status == 'todo'],
                    "in_progress": [t.title for t in viewable_tasks if t.status == 'in_progress'],
                    "done": [t.title for t in viewable_tasks if t.status == 'done']
                }
            }

    async def run(self, user_input: str, history: List[dict] = None) -> AgentState:
        """Executes the orchestrator graph with Langfuse tracing."""
        trace = None
        try:
            trace = self.langfuse.trace(
                name="Orchestrator Run",
                input={"user_input": user_input, "history": history}
            )
        except Exception:
            pass 
        
        initial_state: AgentState = {
            "user_input": user_input,
            "intent": None,
            "history": history or [],
            "response": None,
            "proposed_actions": None,
            "needs_approval": False,
            "notify_user": False
        }
        
        final_state = await self.graph.ainvoke(initial_state)
        
        if trace:
            trace.update(output={"intent": final_state["intent"], "response": final_state["response"]})
        
        return final_state
