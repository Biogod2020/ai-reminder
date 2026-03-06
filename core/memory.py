import os
import json
from typing import List, Dict, Any, Optional
from core.adapter import GeminiAdapter

class MemoryManager:
    """Manages the local Markdown-based memory documents (e.g., user_soul.md)."""

    def __init__(self, soul_file_path: str):
        self.soul_file_path = soul_file_path

    def read_memory(self) -> str:
        if not os.path.exists(self.soul_file_path):
            return ""
        with open(self.soul_file_path, 'r', encoding='utf-8') as f:
            return f.read()

    def update_memory(self, new_content: str, append: bool = True):
        mode = 'a' if append else 'w'
        parent_dir = os.path.dirname(self.soul_file_path)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)
            
        with open(self.soul_file_path, mode, encoding='utf-8') as f:
            if append and os.path.exists(self.soul_file_path) and os.path.getsize(self.soul_file_path) > 0:
                f.write("\n\n")
            f.write(new_content)

class SoulMemory:
    """A lightweight, Markdown-based memory system driven by AI extraction."""

    def __init__(self, soul_file_path: str = "user_soul.md"):
        self.soul_file_path = soul_file_path
        self.manager = MemoryManager(soul_file_path)
        self.adapter = GeminiAdapter()

    async def add_fact(self, raw_input: str, user_id: str = "default_user"):
        """Uses AI to extract structured facts from raw input and updates user_soul.md."""
        prompt = f"Extract concise, atomic facts about the user's habits, preferences, or schedule from this input: '{raw_input}'.\n\nOutput only a list of bullet points starting with '-'."
        
        extracted_facts = await self.adapter.generate_content(prompt)
        
        # Append extracted facts to the Markdown file
        self.manager.update_memory(extracted_facts.strip())

    async def search_facts(self, query: str, user_id: str = "default_user") -> List[Dict[str, Any]]:
        """Searches the memory file using AI-driven context retrieval."""
        content = self.manager.read_memory()
        if not content:
            return []
            
        prompt = f"Given the following user memory content:\n\n{content}\n\nFind facts related to the query: '{query}'.\n\nOutput a JSON list of objects with a 'content' key."
        
        response = await self.adapter.generate_content(prompt)
        
        # Basic JSON extraction
        clean_json = response.strip()
        if "```json" in clean_json:
            clean_json = clean_json.split("```json")[1].split("```")[0].strip()
        elif "```" in clean_json:
            clean_json = clean_json.split("```")[1].split("```")[0].strip()
            
        try:
            return json.loads(clean_json)
        except json.JSONDecodeError:
            return [{"content": response}]
