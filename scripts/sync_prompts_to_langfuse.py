import os
import sys
import logging
import asyncio
from langfuse import Langfuse

# Ensure project root is in path
sys.path.append(os.getcwd())

from core.skills import SkillManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("PromptSync")

async def sync_prompts():
    langfuse = Langfuse(
        public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
        secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
        host=os.getenv("LANGFUSE_HOST")
    )
    
    # 1. Sync System Base Protocol
    system_base = """
    SYSTEM PROTOCOL: HIGH-LEVEL STRATEGIC REASONING
    You are the 'Digital Soul' of the user. 
    
    {{user_context}}

    REASONING STEPS:
    1. STRATEGIC AUDIT: Goal alignment.
    2. COGNITIVE LOAD ESTIMATION: CLT-based assessment.
    3. CIRCADIAN ALIGNMENT: Energy window check.
    
    OUTPUT RULES:
    - Professional, empathetic, scientifically grounded.
    - Prioritize clarity and well-being.
    """
    logger.info("Uploading 'system-base-protocol'...")
    langfuse.create_prompt(
        name="system-base-protocol",
        prompt=system_base.strip()
    )

    # 2. Sync All Skills
    skills_dir = "core/skills"
    manager = SkillManager(skills_dir)
    skills = manager.list_skills()
    
    for skill_name in skills:
        skill_path = os.path.join(skills_dir, skill_name, 'SKILL.md')
        if os.path.exists(skill_path):
            with open(skill_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            prompt_name = f"skill-{skill_name}"
            logger.info(f"Uploading '{prompt_name}'...")
            langfuse.create_prompt(
                name=prompt_name,
                prompt=content.strip()
            )

    logger.info("✨ All prompts synced to Langfuse Cloud!")

if __name__ == "__main__":
    asyncio.run(sync_prompts())
