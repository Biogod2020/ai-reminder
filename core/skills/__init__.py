import os
from typing import List, Optional

class SkillManager:
    """Manages and loads modular AI skill instructions (SKILL.md)."""

    def __init__(self, skills_dir: str):
        """Initializes the SkillManager.

        Args:
            skills_dir: The directory where skill folders are located.
        """
        self.skills_dir = skills_dir

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

    def get_skill_instructions(self, skill_name: str) -> Optional[str]:
        """Retrieves the Markdown instructions for a specific skill.

        Args:
            skill_name: The name of the skill to load.

        Returns:
            The raw text content of the skill's SKILL.md file, or None if not found.
        """
        skill_path = os.path.join(self.skills_dir, skill_name, 'SKILL.md')
        if not os.path.exists(skill_path):
            return None
        with open(skill_path, 'r', encoding='utf-8') as f:
            return f.read()
