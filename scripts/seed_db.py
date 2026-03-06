import os
import sys
# Add project root to path
sys.path.append(os.getcwd())

from core.orchestrator import SoulOrchestrator
from core.models import Task

def seed():
    orchestrator = SoulOrchestrator()
    with orchestrator.Session() as session:
        # Clear existing tasks
        session.query(Task).delete()
        
        tasks = [
            Task(title='Deep Learning Paper Review', cognitive_load_score=0.9, status='todo'),
            Task(title='Respond to Emails', cognitive_load_score=0.2, status='todo'),
            Task(title='Architecture Brainstorming', cognitive_load_score=0.8, status='todo'),
            Task(title='Fill Expense Report', cognitive_load_score=0.1, status='todo'),
            Task(title='Code Review: Feature X', cognitive_load_score=0.7, status='todo'),
            Task(title='Organize Desktop Files', cognitive_load_score=0.3, status='todo'),
        ]
        
        session.add_all(tasks)
        session.commit()
        print(f'Successfully seeded {len(tasks)} tasks into notion_soul.db')

if __name__ == '__main__':
    seed()
