from typing import TypedDict, Optional, List, Any, Dict
from langgraph.graph import StateGraph, END
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from langfuse import Langfuse
from core.adapter import GeminiAdapter
from core.memory import SoulMemory
from core.models import Base, Task
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
        
        # Recursive Persistence: Create parent and child tasks in DB
        with self.Session() as session:
            new_parent = Task(
                title=state["user_input"],
                status='todo',
                sync_status='pending'
            )
            session.add(new_parent)
            session.flush() # Get ID before commit
            
            for st in subtasks:
                child = Task(
                    title=st.get("title", "Untitled Subtask"),
                    parent_id=new_parent.id,
                    cognitive_load_score=st.get("estimated_cognitive_load", 0.0),
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
        """Processes memory-related intents using SoulMemory."""
        await self.memory.add_fact(state["user_input"])
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

    async def classify_intent(self, user_input: str) -> str:
        """Determines the intent of the user's input."""
        prompt = f"Classify the following user input into one of these categories: 'task', 'memory', 'planner', 'clarify'.\n\nInput: {user_input}\n\nOutput only the category name."
        response = await self.adapter.generate_content(prompt)
        clean_response = response.strip().lower()
        if clean_response in ['task', 'memory', 'planner', 'clarify']:
            return clean_response
        return 'clarify'

    async def get_optimized_view(self) -> Dict[str, Any]:
        """Fetches tasks and returns a structured view for the dashboard."""
        with self.Session() as session:
            stmt = select(Task)
            tasks = session.execute(stmt).scalars().all()
            
            # Simple interleaving placeholder for MVP:
            sorted_tasks = sorted(tasks, key=lambda x: x.cognitive_load_score, reverse=True)
            
            calendar_view = []
            for i, t in enumerate(sorted_tasks):
                hour = 9 + i
                calendar_view.append({
                    "id": t.id,
                    "time": f"{hour:02d}:00",
                    "title": t.title,
                    "load": t.cognitive_load_score
                })
                
            return {
                "calendar": calendar_view,
                "kanban": {
                    "todo": [t.title for t in tasks if t.status == 'todo'],
                    "in_progress": [t.title for t in tasks if t.status == 'in_progress'],
                    "done": [t.title for t in tasks if t.status == 'done']
                }
            }

    async def run(self, user_input: str, history: List[dict] = None) -> AgentState:
        """Executes the orchestrator graph with Langfuse tracing."""
        # Safety check for langfuse client initialization
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
        
        # Execute the graph
        final_state = await self.graph.ainvoke(initial_state)
        
        # Update trace with output
        if trace:
            trace.update(output={"intent": final_state["intent"], "response": final_state["response"]})
        
        return final_state
