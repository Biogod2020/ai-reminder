import os
import logging
import asyncio
from typing import Optional, Dict
from langfuse import Langfuse

logger = logging.getLogger("PromptManager")

class PromptManager:
    """
    SOTA Prompt Manager: Local-First with Background Cloud Sync.
    Ensures zero-latency by prioritizing local hardcoded prompts.
    """
    
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(PromptManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.langfuse = Langfuse(
            public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
            secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
            host=os.getenv("LANGFUSE_HOST")
        )
        self.enabled = os.getenv("LANGFUSE_PROMPT_ENABLED", "true").lower() == "true"
        self._cache: Dict[str, str] = {}
        self._sync_tasks = set()
        self._initialized = True

    async def get_prompt(self, name: str, fallback: Optional[str] = None) -> str:
        """
        Returns prompt instantly. 
        Uses: 1. Cache (Cloud version) -> 2. Local Fallback -> 3. Cloud (Block)
        """
        # 1. If we have a cached cloud version from a previous background sync, use it.
        if name in self._cache:
            return self._cache[name]

        # 2. If we have a local fallback, use it IMMEDIATELY to ensure zero latency.
        if fallback:
            # Trigger a background sync so the NEXT time it might use the cloud version
            if self.enabled:
                task = asyncio.create_task(self._sync_prompt_background(name))
                self._sync_tasks.add(task)
                task.add_done_callback(self._sync_tasks.discard)
            return fallback

        # 3. Only block if we have NO fallback at all
        try:
            if not self.enabled: return f"PROMPT_DISABLED_{name}"
            prompt_obj = self.langfuse.get_prompt(name)
            self._cache[name] = prompt_obj.prompt
            return prompt_obj.prompt
        except Exception as e:
            logger.error(f"Critical: No fallback and Langfuse failed for '{name}': {e}")
            return f"MISSING_PROMPT_{name}"

    async def _sync_prompt_background(self, name: str):
        """Fetch and cache prompt without blocking the main flow."""
        try:
            # We use a longer timeout or retry logic here if needed
            # Explicitly try fetching without labels to avoid 404 'production' issues
            prompt_obj = await asyncio.to_thread(self.langfuse.get_prompt, name)
            if prompt_obj:
                self._cache[name] = prompt_obj.prompt
                logger.debug(f"Background sync complete for prompt: {name}")
        except Exception:
            # Silent failure for background sync
            pass

    def flush_cache(self):
        self._cache = {}
