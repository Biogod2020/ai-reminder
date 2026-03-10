import pytest
import os
from fastapi.testclient import TestClient
from core.api import app
from core.models import Base, VizMetadata
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import json

client = TestClient(app)

@pytest.fixture
def test_db():
    # Use a file-based test DB
    test_db_file = "test_viz_api.db"
    if os.path.exists(test_db_file):
        os.remove(test_db_file)
        
    test_db_url = f"sqlite:///{test_db_file}"
    engine = create_engine(test_db_url)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Mock the orchestrator's session in the API.
    from core.api import orchestrator
    original_Session = orchestrator.Session
    orchestrator.Session = Session
    
    # Add a test node
    node = VizMetadata(
        node_id="api_test_node",
        role="API Tester",
        description="Testing API endpoint",
        code_mapping="core/api.py",
        io_schema=json.dumps({"in": "test"}),
        load_metrics=json.dumps({"load": 0.5})
    )
    session.add(node)
    session.commit()
    
    yield session
    
    # Restore and cleanup
    orchestrator.Session = original_Session
    session.close()
    engine.dispose()
    if os.path.exists(test_db_file):
        os.remove(test_db_file)

def test_get_node_metadata(test_db):
    response = client.get("/api/v1/viz/nodes/api_test_node")
    assert response.status_code == 200
    data = response.json()
    assert data["node_id"] == "api_test_node"
    assert data["role"] == "API Tester"

def test_get_node_metadata_not_found(test_db):
    response = client.get("/api/v1/viz/nodes/non_existent_node")
    assert response.status_code == 404

def test_get_all_nodes_metadata(test_db):
    response = client.get("/api/v1/viz/nodes")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(n["node_id"] == "api_test_node" for n in data)
