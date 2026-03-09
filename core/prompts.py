import os
import logging
from typing import Optional, Dict
from langfuse import Langfuse

logger = logging.getLogger("PromptManager")

class PromptManager:
    """Manages dynamic prompts from Langfuse Cloud with local caching and fallback."""
    
    def __init__(self):
        self.langfuse = Langfuse(
            public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
            secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
            host=os.getenv("LANGFUSE_HOST")
        )
        self._cache: Dict[str, str] = {}

    async def get_prompt(self, name: str, fallback: Optional[str] = None) -> str:
        """Fetches a prompt from Langfuse or returns the fallback."""
        if name in self._cache:
            return self._cache[name]
            
        try:
            # Langfuse get_prompt is synchronous in the SDK but thread-safe
            prompt_obj = self.langfuse.get_prompt(name)
            content = prompt_obj.prompt
            self._cache[name] = content
            return content
        except Exception as e:
            logger.warning(f"Failed to fetch prompt '{name}' from Langfuse: {e}")
            return fallback or f"MISSING_PROMPT_{name}"

    def flush_cache(self):
        """Clears the local prompt cache."""
        self._cache = {}
