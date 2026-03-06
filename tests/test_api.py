import pytest
from fastapi.testclient import TestClient
from core.api import app

client = TestClient(app)

def test_api_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@pytest.mark.asyncio
async def test_api_chat_endpoint(mocker):
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
