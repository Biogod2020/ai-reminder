import pytest
from unittest.mock import MagicMock, patch
from core.prompts import PromptManager

@pytest.mark.asyncio
async def test_prompt_fetching_with_fallback():
    """Test that PromptManager fetches from Langfuse and falls back to local if needed."""
    with patch('core.prompts.Langfuse') as MockLangfuse:
        mock_lf = MockLangfuse.return_value
        
        # 1. Success case
        mock_prompt = MagicMock()
        mock_prompt.prompt = "Dynamic prompt"
        mock_lf.get_prompt.return_value = mock_prompt
        
        manager = PromptManager()
        content = await manager.get_prompt("key1")
        assert content == "Dynamic prompt"
        
        # 2. Failure case (different key to avoid cache)
        mock_lf.get_prompt.side_effect = Exception("Network error")
        content = await manager.get_prompt("key2", fallback="Local fallback")
        assert content == "Local fallback"

@pytest.mark.asyncio
async def test_prompt_caching():
    """Test that PromptManager caches prompts locally."""
    with patch('core.prompts.Langfuse') as MockLangfuse:
        mock_lf = MockLangfuse.return_value
        mock_prompt = MagicMock()
        mock_prompt.prompt = "Cached prompt"
        mock_lf.get_prompt.return_value = mock_prompt
        
        manager = PromptManager()
        await manager.get_prompt("cached-key")
        await manager.get_prompt("cached-key")
        
        # Should only call Langfuse once
        mock_lf.get_prompt.assert_called_once_with("cached-key")
