import os
import json
import asyncio
import logging
from typing import List, Dict, Any
from core.memory import SoulMemory

logger = logging.getLogger("InitializationQA")

class InitializationManager:
    """Manages the interactive Q&A session to bootstrap the user's Soul profile."""
    
    def __init__(self):
        self.soul_memory = SoulMemory()
        self.questions = [
            {
                "id": "circadian_rhythm",
                "question": "What are your typical wake-up and sleep times?",
                "placeholder": "e.g., Wake up at 7:30 AM, sleep at 11:00 PM",
                "scope": "soul"
            },
            {
                "id": "peak_productivity",
                "question": "When do you feel most focused and productive during the day?",
                "placeholder": "e.g., Morning (9 AM - 12 PM) or Late night",
                "scope": "soul"
            },
            {
                "id": "work_preferences",
                "question": "What kind of tasks do you prefer to tackle first?",
                "placeholder": "e.g., Deep work/coding first, or clear easy emails first",
                "scope": "soul"
            },
            {
                "id": "notification_style",
                "question": "How do you prefer to be nudged about upcoming tasks?",
                "placeholder": "e.g., Direct and brief, or encouraging and descriptive",
                "scope": "soul"
            },
            {
                "id": "goals",
                "question": "What are your primary goals for this month?",
                "placeholder": "e.g., Complete the memory module, learn Swift",
                "scope": "soul"
            }
        ]

    async def run_cli_session(self):
        """Runs the Q&A session via CLI."""
        print("\n--- 🧘 Notion-Soul-Agent Initialization ---")
        print("Help me understand your habits to serve you better.\n")
        
        results = {}
        for q in self.questions:
            print(f"Question: {q['question']}")
            answer = input(f"Answer ({q['placeholder']}): ").strip()
            if not answer:
                answer = "No specific preference provided."
            
            results[q['id']] = answer
            
            # Store each answer immediately as a fact
            await self.soul_memory.add_fact(f"User preference for {q['id']}: {answer}", scope=q['scope'])
            print(f"✓ Remembered.\n")
            
        print("--- Initialization Complete! Your Soul Context has been updated. ---\n")
        return results

if __name__ == "__main__":
    # This allows running the init script directly
    manager = InitializationManager()
    asyncio.run(manager.run_cli_session())
