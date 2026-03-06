import os
from typing import List, Optional

class SkillManager:
    def __init__(self, skills_dir: str):
        self.skills_dir = skills_dir

    def list_skills(self) -> List[str]:
        if not os.path.exists(self.skills_dir):
            return []
        return [
            d for d in os.listdir(self.skills_dir)
            if os.path.isdir(os.path.join(self.skills_dir, d))
        ]

    def get_skill_instructions(self, skill_name: str) -> Optional[str]:
        skill_path = os.path.join(self.skills_dir, skill_name, 'SKILL.md')
        if not os.path.exists(skill_path):
            return None
        with open(skill_path, 'r', encoding='utf-8') as f:
            return f.read()
