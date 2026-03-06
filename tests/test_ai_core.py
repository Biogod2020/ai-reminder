import os
import pytest
from core.skills import SkillManager
from core.memory import MemoryManager
from core.models import Base, Task
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture
def db_session():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

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

def test_task_recursion(db_session):
    parent = Task(title='Parent Task')
    db_session.add(parent)
    db_session.commit()
    
    child = Task(title='Child Task', parent_id=parent.id)
    db_session.add(child)
    db_session.commit()
    
    assert child.parent_id == parent.id

def test_memory_manager_soul(tmp_path):
    soul_file = tmp_path / 'user_soul.md'
    mm = MemoryManager(str(soul_file))
    
    mm.update_memory('User prefers morning work.')
    content = mm.read_memory()
    assert 'User prefers morning work.' in content
