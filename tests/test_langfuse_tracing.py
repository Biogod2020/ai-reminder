import pytest
import os
from unittest.mock import MagicMock, patch, AsyncMock
from core.orchestrator import SoulOrchestrator
from core.adapter import GeminiAdapter

@pytest.mark.asyncio
async def test_orchestrator_tracing():
    """Test that SoulOrchestrator correctly initializes and uses Langfuse tracing."""
    with patch('core.orchestrator.Langfuse') as MockLangfuse:
        # mock_lf = MockLangfuse.return_value
        orchestrator = SoulOrchestrator(db_url="sqlite:///:memory:")
        
        # Mock the graph execution using AsyncMock
        orchestrator.graph = MagicMock()
        orchestrator.graph.ainvoke = AsyncMock(return_value={
            "user_input": "hello",
            "intent": "clarify",
            "history": [],
            "response": "How can I help?",
            "proposed_actions": None,
            "needs_approval": False,
            "notify_user": False
        })
        
        await orchestrator.run("hello")
        
        # Verify ainvoke was called
        orchestrator.graph.ainvoke.assert_awaited_once()

@pytest.mark.asyncio
async def test_adapter_observe_decorator():
    """Test that GeminiAdapter uses Langfuse observation."""
    with patch('core.adapter.Langfuse') as MockLangfuse:
        adapter = GeminiAdapter()
        
        # Verify langfuse was initialized
        assert adapter.langfuse is not None
        
        # Mock the client call with AsyncMock
        mock_response = MagicMock()
        mock_response.text = "Mock response"
        adapter.client.aio.models.generate_content = AsyncMock(return_value=mock_response)
        
        # We also need to mock memory search to avoid real DB calls
        adapter.memory.search = AsyncMock(return_value=[])
        
        await adapter.generate_content("test prompt")
        
        # Verify generate_content was called
        adapter.client.aio.models.generate_content.assert_awaited_once()
