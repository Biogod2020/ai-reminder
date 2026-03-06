import os
import pytest
from core.skills import SkillManager
from core.memory import MemoryManager, SoulMemory
from core.models import Base, Task
from core.adapter import GeminiAdapter
from core.orchestrator import SoulOrchestrator
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

@pytest.fixture
def db_url(tmp_path):
    return f"sqlite:///{tmp_path}/test_soul.db"

@pytest.fixture
def orchestrator(db_url):
    return SoulOrchestrator(db_url=db_url)

def test_skill_manager_load():
    # Setup a dummy skill
    skill_path = 'core/skills/test-skill'
    os.makedirs(skill_path, exist_ok=True)
    with open(os.path.join(skill_path, 'SKILL.md'), 'w') as f:
        f.write('---\nname: test-skill\ndescription: a test skill\n---\n# Test Skill Instructions')
    
    sm = SkillManager('core/skills')
    skills = sm.list_skills()
    assert 'test-skill' in skills
    
    instructions = sm.get_skill_instructions('test-skill')
    assert '# Test Skill Instructions' in instructions

def test_task_recursion():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    with Session() as session:
        parent = Task(title='Parent Task')
        session.add(parent)
        session.commit()
        
        child = Task(title='Child Task', parent_id=parent.id)
        session.add(child)
        session.commit()
        
        assert child.parent_id == parent.id

def test_memory_manager_soul(tmp_path):
    soul_file = tmp_path / 'user_soul.md'
    mm = MemoryManager(str(soul_file))
    
    mm.update_memory('User prefers morning work.')
    content = mm.read_memory()
    assert 'User prefers morning work.' in content

@pytest.mark.asyncio
async def test_orchestrator_persistence_task(orchestrator, mocker):
    # Mock decomposition to return fixed subtasks
    mock_adapter = mocker.patch.object(orchestrator.adapter, 'decompose_task')
    mock_adapter.return_value = [
        {"title": "Subtask A", "estimated_cognitive_load": 0.4},
        {"title": "Subtask B", "estimated_cognitive_load": 0.6}
    ]
    # Mock classification
    mocker.patch.object(orchestrator.adapter, 'generate_content', return_value='task')

    # Run orchestrator
    state = await orchestrator.run("Large Research Task")
    
    # Verify subtasks are in proposed_actions
    assert len(state["proposed_actions"]) == 2
    
    # Implementation Phase 2: Check if parent task was created in DB
    with orchestrator.Session() as session:
        stmt = select(Task).where(Task.title == "Large Research Task")
        parent = session.execute(stmt).scalar_one_or_none()
        assert parent is not None
        assert parent.status == "todo"
        
        # Verify subtasks are persisted and linked
        stmt_sub = select(Task).where(Task.parent_id == parent.id)
        children = session.execute(stmt_sub).scalars().all()
        assert len(children) == 2
        titles = [c.title for c in children]
        assert "Subtask A" in titles
        assert "Subtask B" in titles
