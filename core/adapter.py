import os
import json
import logging
from typing import Optional, List, Any, Dict
from google import genai
from langfuse import Langfuse, observe
from core.skills import SkillManager
from core.memory import SharedMemoryManager
from core.prompts import PromptManager

logger = logging.getLogger("GeminiAdapter")


class GeminiAdapter:
    """Adapter for Gemini AI models with skill support and proxy optimization."""

    def __init__(
        self, 
        api_key: Optional[str] = None, 
        base_url: Optional[str] = None, 
        skills_dir: str = 'core/skills'
    ):
        """Initializes the GeminiAdapter with shared memory access."""
        use_local_proxy = os.getenv('USE_LOCAL_PROXY', 'false').lower() == "true"
        proxy_password = os.getenv('PROXY_PASSWORD', '123456')
        
        if use_local_proxy:
            self.api_key = proxy_password
            self.base_url = base_url or os.getenv(
                'LOCAL_PROXY_URL', 
                'http://localhost:8888'
            )
            self.model_id = 'gemini-3-flash-preview'
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
        self.prompt_manager = PromptManager()
        
        # Initialize Langfuse
        self.langfuse = Langfuse(
            public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
            secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
            host=os.getenv("LANGFUSE_HOST")
        )

    @observe()
    async def generate_content(
        self, 
        prompt: str, 
        images: Optional[List[Any]] = None, 
        skill_name: Optional[str] = None, 
        include_memory: bool = True
    ) -> str:
        """Generates content asynchronously with injected context.
        
        Args:
            prompt: The user's input prompt.
            images: Optional list of image data.
            skill_name: Optional name of the skill to mount.
            include_memory: Whether to inject relevant user memory context.
        """
        user_context = ""
        if include_memory:
            try:
                memories = await self.memory.search(prompt, scope="soul")
                if memories:
                    facts = "\n".join([f"- {m.get('content', '')}" for m in memories[:5]])
                    user_context = f"\nRELEVANT USER CONTEXT:\n{facts}"
            except Exception as e:
                logger.error(f"Failed to fetch memory for context: {e}")

        base_protocol_fallback = f"""
        SYSTEM PROTOCOL: HIGH-LEVEL STRATEGIC REASONING
        You are the 'Digital Soul' of the user. 
        
        {user_context}

        REASONING STEPS:
        1. STRATEGIC AUDIT: Goal alignment.
        2. COGNITIVE LOAD ESTIMATION: CLT-based assessment.
        3. CIRCADIAN ALIGNMENT: Energy window check.
        
        OUTPUT RULES:
        - Professional, empathetic, scientifically grounded.
        - Prioritize clarity and well-being.
        """
        
        # Fetch base protocol dynamically
        base_protocol = await self.prompt_manager.get_prompt("system-base-protocol", fallback=base_protocol_fallback)
        
        # If the dynamic prompt contains placeholders, we should ideally handle them here.
        # For simplicity, we assume the dynamic prompt is already formatted or handles context.
        
        skill_instruction = ""
        if skill_name:
            skill_instruction = await self.skill_manager.get_skill_instructions(skill_name)
        
        combined_instruction = base_protocol + "\n\n" + (skill_instruction or "")

        content = [prompt]
        if images:
            content.extend(images)
        
        response = await self.client.aio.models.generate_content(
            model=self.model_id,
            contents=content,
            config={'system_instruction': combined_instruction}
        )
        return response.text

    async def decompose_task(
        self, 
        task_title: str, 
        context: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Decomposes a task into atomic sub-tasks."""
        prompt = f"Please decompose the following task: '{task_title}'."
        if context:
            prompt += f"\n\nAdditional User Context:\n{context}"
        
        prompt += "\n\nOutput only a JSON list of sub-tasks."
        
        response_text = await self.generate_content(
            prompt, 
            skill_name='task-atomizer'
        )
        
        clean_json = response_text.strip()
        if "```json" in clean_json:
            clean_json = clean_json.split("```json")[1].split("```")[0].strip()
        elif "```" in clean_json:
            clean_json = clean_json.split("```")[1].split("```")[0].strip()
            
        try:
            return json.loads(clean_json)
        except json.JSONDecodeError:
            return [{"title": "Error parsing AI response", "raw": response_text}]
