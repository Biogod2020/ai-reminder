import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.models import Base, Task, UserSoul
from core.adapter import GeminiAdapter
import os

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

@pytest.mark.asyncio
async def test_gemini_adapter_init(mocker):
    # Clear proxy env vars to test direct init
    mocker.patch.dict(os.environ, {"USE_LOCAL_PROXY": "false"}, clear=False)
    adapter = GeminiAdapter(api_key='fake-key', base_url='https://custom.api')
    assert adapter.api_key == 'fake-key'
    assert adapter.base_url == 'https://custom.api'

@pytest.mark.asyncio
async def test_gemini_adapter_generate_text(mocker):
    # Mock the Client
    mock_client_class = mocker.patch('core.adapter.genai.Client')
    mock_client = mock_client_class.return_value
    mock_response = mocker.Mock()
    mock_response.text = 'Mocked Response'
    
    # Mock client.aio.models.generate_content
    mock_client.aio.models.generate_content = mocker.AsyncMock(return_value=mock_response)

    adapter = GeminiAdapter(api_key='fake-key')
    response = await adapter.generate_content('Test Prompt')
    
    assert response == 'Mocked Response'
    mock_client.aio.models.generate_content.assert_called_once()

@pytest.mark.asyncio
async def test_gemini_adapter_proxy_config(mocker):
    # Test if adapter correctly picks up proxy settings
    mocker.patch.dict(os.environ, {"USE_LOCAL_PROXY": "true", "PROXY_PASSWORD": "123"}, clear=False)
    adapter = GeminiAdapter(api_key='fake-key', base_url='http://localhost:8888')
    assert adapter.base_url == 'http://localhost:8888'
    assert adapter.api_key == '123'

@pytest.mark.asyncio
async def test_gemini_adapter_proxy_request(mocker):
    mock_client_class = mocker.patch('core.adapter.genai.Client')
    mock_client = mock_client_class.return_value
    mock_response = mocker.Mock()
    mock_response.text = 'Proxy Response'
    mock_client.aio.models.generate_content = mocker.AsyncMock(return_value=mock_response)

    mocker.patch.dict(os.environ, {"USE_LOCAL_PROXY": "true", "PROXY_PASSWORD": "123456"}, clear=False)
    
    adapter = GeminiAdapter(api_key='fake-key', base_url='http://localhost:8888')
    await adapter.generate_content('test')
    
    # Verify Client initialization args
    args, kwargs = mock_client_class.call_args
    assert kwargs['http_options']['base_url'] == 'http://localhost:8888'

def test_task_duration_and_slack(db_session):
    task = Task(
        title='Timed Task',
        duration_minutes=45,
        slack_minutes=10
    )
    db_session.add(task)
    db_session.commit()
    
    retrieved = db_session.query(Task).filter_by(title='Timed Task').first()
    assert retrieved.duration_minutes == 45
    assert retrieved.slack_minutes == 10
