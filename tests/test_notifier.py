import pytest
import httpx
from core.notifier import Notifier

@pytest.mark.asyncio
async def test_notifier_bark_send(respx_mock):
    # Mock Bark API response
    respx_mock.get("https://api.day.app/fake-key/Test%20Title/Test%20Body").mock(
        return_value=httpx.Response(200, json={"code": 200, "message": "success"})
    )
    
    notifier = Notifier(bark_key="fake-key")
    success = await notifier.send_bark("Test Title", "Test Body")
    
    assert success is True
