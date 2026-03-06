import os
import json
from typing import Optional, List, Any, Dict
from google import genai
from core.skills import SkillManager

class GeminiAdapter:
    """Adapter for interacting with Google's Gemini AI models with skill support."""

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
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        self.base_url = base_url
        
        if not self.api_key:
            raise ValueError('GEMINI_API_KEY must be provided or set in environment')

        http_options = {}
        if self.base_url:
            http_options['base_url'] = self.base_url

        self.client = genai.Client(
            api_key=self.api_key,
            http_options=http_options if http_options else None
        )
        self.model_id = 'gemini-1.5-flash-latest'
        self.skill_manager = SkillManager(skills_dir)

    async def generate_content(self, prompt: str, images: Optional[List[Any]] = None, skill_name: Optional[str] = None) -> str:
        """Generates content asynchronously, supporting optional skill mounting.

        Args:
            prompt: The text prompt to send to the model.
            images: Optional list of image data to include in the request.
            skill_name: Optional name of a skill to mount as a system instruction.

        Returns:
            The generated text response.
        """
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
        """Decomposes a task into atomic sub-tasks using the task-atomizer skill.

        Args:
            task_title: The title of the task to decompose.
            context: Optional additional user context to inform the decomposition.

        Returns:
            A list of dictionaries, each representing an atomic sub-task.
        """
        prompt = f"Please decompose the following task: '{task_title}'."
        if context:
            prompt += f"\n\nAdditional User Context:\n{context}"
        
        prompt += "\n\nOutput only a JSON list of sub-tasks as defined in your instructions."
        
        # We use the 'task-atomizer' skill for this request
        response_text = await self.generate_content(prompt, skill_name='task-atomizer')
        
        # Basic JSON extraction (Gemini might wrap it in markdown blocks)
        clean_json = response_text.strip()
        if clean_json.startswith("```json"):
            clean_json = clean_json.split("```json")[1].split("```")[0].strip()
        elif clean_json.startswith("```"):
            clean_json = clean_json.split("```")[1].split("```")[0].strip()
            
        try:
            return json.loads(clean_json)
        except json.JSONDecodeError:
            # Fallback or error handling could go here
            return [{"title": "Error parsing AI response", "raw": response_text}]
