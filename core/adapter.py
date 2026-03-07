import os
import json
import logging
from typing import Optional, List, Any, Dict
from google import genai
from core.skills import SkillManager
from core.memory import SharedMemoryManager

logger = logging.getLogger("GeminiAdapter")

class GeminiAdapter:
    """Adapter for interacting with Google's Gemini AI models with skill support and proxy optimization."""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, skills_dir: str = 'core/skills'):
        """Initializes the GeminiAdapter with shared memory access."""
        use_local_proxy = os.getenv('USE_LOCAL_PROXY', 'false').lower() == 'true'
        proxy_password = os.getenv('PROXY_PASSWORD', '123456')
        
        # If using proxy, the 'api_key' for the client should be the proxy password
        if use_local_proxy:
            self.api_key = proxy_password
            self.base_url = base_url or os.getenv('LOCAL_PROXY_URL', 'http://localhost:8888')
            self.model_id = 'gemini-3-flash-preview' # SOTA model supported by proxy
        else:
            self.api_key = api_key or os.getenv('GEMINI_API_KEY')
            self.base_url = base_url
            self.model_id = 'gemini-3.1-flash-lite-preview'

        if not self.api_key:
            raise ValueError('GEMINI_API_KEY (or PROXY_PASSWORD) must be provided')

        http_options = {}
        if self.base_url:
            http_options['base_url'] = self.base_url

        self.client = genai.Client(
            api_key=self.api_key,
            http_options=http_options if http_options else None
        )
        self.skill_manager = SkillManager(skills_dir)
        self.memory = SharedMemoryManager()

    async def generate_content(self, prompt: str, images: Optional[List[Any]] = None, skill_name: Optional[str] = None, include_memory: bool = True) -> str:
        """Generates content asynchronously, enforcing High-Level Reasoning Protocol and injected context."""
        
        user_context = ""
        if include_memory:
            # Fetch recent relevant context from shared memory
            try:
                memories = await self.memory.search(prompt, scope="soul")
                if memories:
                    user_context = "\nRELEVANT USER CONTEXT:\n" + "\n".join([f"- {m.get('content', '')}" for m in memories[:5]])
            except Exception as e:
                logger.error(f"Failed to fetch memory for context: {e}")

        base_protocol = f"""
        SYSTEM PROTOCOL: HIGH-LEVEL STRATEGIC REASONING
        You are the 'Digital Soul' of the user. You do not just process text; you reason about human potential and cognitive limits.
        
        {user_context}

        REASONING STEPS:
        1. STRATEGIC AUDIT: What is the user's ultimate goal? How does this request serve it?
        2. COGNITIVE LOAD ESTIMATION: Based on CLT (Cognitive Load Theory), how taxing is this?
        3. CIRCADIAN ALIGNMENT: Is this the right time of day for this specific task?
        
        OUTPUT RULES:
        - Be professional, empathetic, and scientifically grounded.
        - ALWAYS prioritize clarity and mental well-being.
        """
        
        skill_instruction = ""
        if skill_name:
            skill_instruction = self.skill_manager.get_skill_instructions(skill_name)
        
        combined_instruction = base_protocol + "\n\n" + skill_instruction

        content = [prompt]
        if images:
            content.extend(images)
        
        response = await self.client.aio.models.generate_content(
            model=self.model_id,
            contents=content,
            config={'system_instruction': combined_instruction}
        )
        return response.text

    async def decompose_task(self, task_title: str, context: Optional[str] = None) -> List[Dict[str, Any]]:
        """Decomposes a task into atomic sub-tasks using the task-atomizer skill."""
        prompt = f"Please decompose the following task: '{task_title}'."
        if context:
            prompt += f"\n\nAdditional User Context:\n{context}"
        
        prompt += "\n\nOutput only a JSON list of sub-tasks as defined in your instructions."
        
        # We use the 'task-atomizer' skill for this request
        response_text = await self.generate_content(prompt, skill_name='task-atomizer')
        
        # Basic JSON extraction
        clean_json = response_text.strip()
        if "```json" in clean_json:
            clean_json = clean_json.split("```json")[1].split("```")[0].strip()
        elif "```" in clean_json:
            clean_json = clean_json.split("```")[1].split("```")[0].strip()
            
        try:
            return json.loads(clean_json)
        except json.JSONDecodeError:
            return [{"title": "Error parsing AI response", "raw": response_text}]
