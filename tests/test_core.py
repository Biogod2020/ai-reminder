import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.models import Base, Task, UserSoul

@pytest.fixture
def db_session():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_create_task(db_session):
    task = Task(
        title='Test Task',
        notion_id='notion-123',
        status='todo',
        cognitive_load_score=0.5,
        sync_status='synced'
    )
    db_session.add(task)
    db_session.commit()
    
    retrieved = db_session.query(Task).filter_by(title='Test Task').first()
    assert retrieved.title == 'Test Task'
    assert retrieved.cognitive_load_score == 0.5

def test_create_user_soul(db_session):
    soul = UserSoul(
        key='habit_preference',
        value='morning_person',
        category='habit'
    )
    db_session.add(soul)
    db_session.commit()
    
    retrieved = db_session.query(UserSoul).filter_by(key='habit_preference').first()
    assert retrieved.value == 'morning_person'
