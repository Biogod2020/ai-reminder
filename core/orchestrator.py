from typing import TypedDict, Optional, List, Any, Dict
from langgraph.graph import StateGraph, END
from core.adapter import GeminiAdapter
from core.memory import SoulMemory

class AgentState(TypedDict):
    user_input: str
    intent: Optional[str]
    history: List[dict]
    response: Optional[str]
    proposed_actions: Optional[List[Dict[str, Any]]]
    needs_approval: bool

class SoulOrchestrator:
    """Orchestrates natural language intents using a LangGraph state machine."""

    def __init__(self):
        self.adapter = GeminiAdapter()
        self.memory = SoulMemory()
        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(AgentState)

        # Define nodes
        workflow.add_node("classify", self._node_classify)
        workflow.add_node("handle_task", self._node_handle_task)
        workflow.add_node("handle_memory", self._node_handle_memory)
        workflow.add_node("handle_planner", self._node_handle_planner)
        workflow.add_node("handle_clarify", self._node_handle_clarify)
        workflow.add_node("await_approval", self._node_await_approval)

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

        # Handle task and memory might need approval
        workflow.add_edge("handle_task", "await_approval")
        workflow.add_edge("handle_memory", END) # Memory updates are direct for now
        workflow.add_edge("handle_planner", "await_approval")
        workflow.add_edge("handle_clarify", END)
        workflow.add_edge("await_approval", END)

        return workflow.compile()

    async def _node_classify(self, state: AgentState) -> AgentState:
        """Classifies the user's intent."""
        intent = await self.classify_intent(state["user_input"])
        return {**state, "intent": intent}

    def _route_intent(self, state: AgentState) -> str:
        """Routes to the appropriate node based on intent."""
        return state["intent"] or "clarify"

    async def _node_handle_task(self, state: AgentState) -> AgentState:
        """Decomposes a task and proposes actions."""
        subtasks = await self.adapter.decompose_task(state["user_input"])
        return {
            **state, 
            "proposed_actions": subtasks, 
            "needs_approval": True,
            "response": f"I've broken down '{state['user_input']}' into {len(subtasks)} atomic steps. Please approve the plan."
        }

    async def _node_handle_memory(self, state: AgentState) -> AgentState:
        """Processes memory-related intents using SoulMemory."""
        await self.memory.add_fact(state["user_input"])
        return {**state, "response": "I've updated your 'Digital Soul' with this information."}

    async def _node_handle_planner(self, state: AgentState) -> AgentState:
        return {**state, "response": "Planning logic pending Implementation Phase 3."}

    async def _node_handle_clarify(self, state: AgentState) -> AgentState:
        return {**state, "response": "I'm not quite sure what you mean. Could you provide more details?"}

    async def _node_await_approval(self, state: AgentState) -> AgentState:
        """Node representing the state where the agent is waiting for user confirmation."""
        return {**state, "response": state.get("response", "Waiting for your approval.")}

    async def classify_intent(self, user_input: str) -> str:
        """Determines the intent of the user's input."""
        prompt = f"Classify the following user input into one of these categories: 'task', 'memory', 'planner', 'clarify'.\n\nInput: {user_input}\n\nOutput only the category name."
        response = await self.adapter.generate_content(prompt)
        clean_response = response.strip().lower()
        if clean_response in ['task', 'memory', 'planner', 'clarify']:
            return clean_response
        return 'clarify'

    async def run(self, user_input: str, history: List[dict] = None) -> AgentState:
        """Executes the orchestrator graph."""
        initial_state: AgentState = {
            "user_input": user_input,
            "intent": None,
            "history": history or [],
            "response": None,
            "proposed_actions": None,
            "needs_approval": False
        }
        return await self.graph.ainvoke(initial_state)
