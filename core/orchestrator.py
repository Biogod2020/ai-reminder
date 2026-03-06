from typing import TypedDict, Optional, List
from langgraph.graph import StateGraph, END
from core.adapter import GeminiAdapter

class AgentState(TypedDict):
    user_input: str
    intent: Optional[str]
    history: List[dict]
    response: Optional[str]

class SoulOrchestrator:
    """Orchestrates natural language intents using a LangGraph state machine."""

    def __init__(self):
        self.adapter = GeminiAdapter()
        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(AgentState)

        # Define nodes
        workflow.add_node("classify", self._node_classify)
        workflow.add_node("handle_task", self._node_handle_task)
        workflow.add_node("handle_memory", self._node_handle_memory)
        workflow.add_node("handle_planner", self._node_handle_planner)
        workflow.add_node("handle_clarify", self._node_handle_clarify)

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

        # Connect handlers to END
        workflow.add_edge("handle_task", END)
        workflow.add_edge("handle_memory", END)
        workflow.add_edge("handle_planner", END)
        workflow.add_edge("handle_clarify", END)

        return workflow.compile()

    async def _node_classify(self, state: AgentState) -> AgentState:
        """Classifies the user's intent."""
        intent = await self.classify_intent(state["user_input"])
        return {**state, "intent": intent}

    def _route_intent(self, state: AgentState) -> str:
        """Routes to the appropriate node based on intent."""
        return state["intent"] or "clarify"

    async def _node_handle_task(self, state: AgentState) -> AgentState:
        return {**state, "response": "Handling task..."}

    async def _node_handle_memory(self, state: AgentState) -> AgentState:
        return {**state, "response": "Handling memory..."}

    async def _node_handle_planner(self, state: AgentState) -> AgentState:
        return {**state, "response": "Handling planning..."}

    async def _node_handle_clarify(self, state: AgentState) -> AgentState:
        return {**state, "response": "Need more info."}

    async def classify_intent(self, user_input: str) -> str:
        """Determines the intent of the user's input."""
        prompt = f"Classify the following user input into one of these categories: 'task', 'memory', 'planner', 'clarify'.\n\nInput: {user_input}\n\nOutput only the category name."
        # Use simple classification for now
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
            "response": None
        }
        return await self.graph.ainvoke(initial_state)
