import pytest
from core.orchestrator import SoulOrchestrator

@pytest.mark.asyncio
async def test_orchestrator_initialization():
    orchestrator = SoulOrchestrator()
    assert orchestrator.graph is not None

@pytest.mark.asyncio
async def test_classify_intent_task(mocker):
    # Mock GeminiAdapter to return a task-related classification
    mock_adapter = mocker.patch('core.orchestrator.GeminiAdapter')
    mock_instance = mock_adapter.return_value
    mock_instance.generate_content = mocker.AsyncMock(return_value='task')
    
    orchestrator = SoulOrchestrator()
    intent = await orchestrator.classify_intent("I need to write a report")
    assert intent == "task"

@pytest.mark.asyncio
async def test_classify_intent_memory(mocker):
    mock_adapter = mocker.patch('core.orchestrator.GeminiAdapter')
    mock_instance = mock_adapter.return_value
    mock_instance.generate_content = mocker.AsyncMock(return_value='memory')
    
    orchestrator = SoulOrchestrator()
    intent = await orchestrator.classify_intent("Remember that I like coffee")
    assert intent == "memory"
