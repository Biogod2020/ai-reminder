import os
from typing import List, Optional
from core.prompts import PromptManager

class SkillManager:
    """Manages and loads modular AI skill instructions (SKILL.md)."""

    def __init__(self, skills_dir: str):
        """Initializes the SkillManager.

        Args:
            skills_dir: The directory where skill folders are located.
        """
        self.skills_dir = skills_dir
        self.prompt_manager = PromptManager()

    def list_skills(self) -> List[str]:
        """Lists all available skills in the skills directory.

        Returns:
            A list of skill names (folder names).
        """
        if not os.path.exists(self.skills_dir):
            return []
        return [
            d for d in os.listdir(self.skills_dir)
            if os.path.isdir(os.path.join(self.skills_dir, d))
        ]

    async def get_skill_instructions(self, skill_name: str) -> Optional[str]:
        """Retrieves the instructions for a specific skill (Langfuse first, then local fallback)."""
        # 1. Try local file to get fallback content
        local_content = None
        skill_path = os.path.join(self.skills_dir, skill_name, 'SKILL.md')
        if os.path.exists(skill_path):
            with open(skill_path, 'r', encoding='utf-8') as f:
                local_content = f.read()
        
        # 2. Fetch from Langfuse with local fallback
        # Key convention: skill-<name>
        return await self.prompt_manager.get_prompt(f"skill-{skill_name}", fallback=local_content)
