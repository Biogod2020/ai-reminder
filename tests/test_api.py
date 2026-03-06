import pytest
from fastapi.testclient import TestClient
from core.api import app
from core.models import Task
from sqlalchemy import select

client = TestClient(app)

def test_api_health_check():
    """Verifies that the health check endpoint is responsive."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@pytest.mark.asyncio
async def test_api_chat_endpoint(mocker):
    """Verifies that the chat endpoint correctly routes intents and returns responses."""
    # Mock the orchestrator to avoid real AI calls
    mock_orch = mocker.patch("core.api.orchestrator")
    mock_orch.run = mocker.AsyncMock(return_value={
        "intent": "task",
        "response": "Mocked response",
        "proposed_actions": None
    })
    
    response = client.post("/chat", json={"message": "test message"})
    assert response.status_code == 200
    assert response.json()["intent"] == "task"

@pytest.mark.asyncio
async def test_api_get_view_data(mocker):
    """Verifies that the view data endpoint returns structured JSON."""
    # Mock the orchestrator to return structured view data
    mock_orch = mocker.patch("core.api.orchestrator")
    mock_orch.get_optimized_view = mocker.AsyncMock(return_value={
        "calendar": [{"time": "09:00", "title": "Task 1", "load": 0.8}],
        "kanban": {"todo": ["Task 2"]}
    })
    
    response = client.get("/get_view_data")
    assert response.status_code == 200
    assert "calendar" in response.json()
    assert "kanban" in response.json()

@pytest.mark.asyncio
async def test_api_end_to_end_task_flow(mocker):
    """Verifies the full flow from chat input to database persistence and retrieval."""
    # 1. Setup mock for Gemini decomposition
    mock_adapter = mocker.patch("core.orchestrator.GeminiAdapter")
    mock_inst = mock_adapter.return_value
    mock_inst.generate_content = mocker.AsyncMock(return_value="task")
    mock_inst.decompose_task = mocker.AsyncMock(return_value=[
        {"title": "Subtask 1", "estimated_cognitive_load": 0.5}
    ])
    
    # 2. Call chat API to create a task
    response = client.post("/chat", json={"message": "Build a rocket"})
    assert response.status_code == 200
    assert response.json()["intent"] == "task"
    
    # 3. Call get_view_data to verify persistence in results
    # We don't mock get_optimized_view here to test the real DB integration
    view_response = client.get("/get_view_data")
    assert view_response.status_code == 200
    calendar = view_response.json()["calendar"]
    assert any("Build a rocket" in item["title"] for item in calendar)
