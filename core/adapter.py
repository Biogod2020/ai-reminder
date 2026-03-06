import os
import json
from typing import Optional, List, Any, Dict
from google import genai
from core.skills import SkillManager

class GeminiAdapter:
    """Adapter for interacting with Google's Gemini AI models with skill support and proxy optimization."""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, skills_dir: str = 'core/skills'):
        """Initializes the GeminiAdapter.

        Args:
            api_key: The Google AI API key. If not provided, it will be read from the
                GEMINI_API_KEY environment variable.
            base_url: Optional custom base URL for the API.
            skills_dir: The directory where skill definitions are stored.

        Raises:
            ValueError: If no API key is provided or found in the environment.
        """
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

    async def generate_content(self, prompt: str, images: Optional[List[Any]] = None, skill_name: Optional[str] = None) -> str:
        """Generates content asynchronously, supporting optional skill mounting."""
        system_instruction = None
        if skill_name:
            system_instruction = self.skill_manager.get_skill_instructions(skill_name)

        content = [prompt]
        if images:
            content.extend(images)
        
        response = await self.client.aio.models.generate_content(
            model=self.model_id,
            contents=content,
            config={'system_instruction': system_instruction} if system_instruction else None
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
