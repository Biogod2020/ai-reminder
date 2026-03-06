import pytest
import os
from core.orchestrator import SoulOrchestrator
from core.models import Base, Task
from datetime import datetime, timezone

@pytest.fixture
def db_url(tmp_path):
    return f"sqlite:///{tmp_path}/test_soul.db"

@pytest.fixture
def orchestrator(db_url):
    return SoulOrchestrator(db_url=db_url)

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

@pytest.mark.asyncio
async def test_orchestrator_heartbeat_nudge(orchestrator, mocker):
    # 1. Seed an active task that is nearing its end
    with orchestrator.Session() as session:
        task = Task(title='Active Task', status='in_progress', duration_minutes=30, created_at=datetime.now(timezone.utc))
        session.add(task)
        session.commit()

    # 2. Run heartbeat node evaluation logic (mocking AI)
    # Note: We need to mock the adapter inside the orchestrator
    mock_adapter = mocker.patch.object(orchestrator.adapter, 'generate_content', new_callable=mocker.AsyncMock)
    mock_adapter.return_value = '{"nudge_message": "Is it done?", "suggested_action": "Continue"}'
    
    # Trigger nudge evaluation
    result = await orchestrator.evaluate_nudge()
    assert result['nudge_needed'] is True
    assert "Is it done?" in result['message']
