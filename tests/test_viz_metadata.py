import pytest
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from core.models import Base, VizMetadata

@pytest.fixture
def session():
    # Use in-memory SQLite for testing to avoid side effects
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_viz_metadata_create_and_read(session):
    """Tests basic CRUD - Create and Read."""
    node = VizMetadata(
        node_id="test_node",
        role="Tester",
        description="A node for testing purposes",
        code_mapping="tests/test_viz_metadata.py",
        io_schema=json.dumps({"input": "test_data", "output": "test_result"}),
        load_metrics=json.dumps({"cognitive_load": 0.1, "energy": "low"}),
        metadata_json=json.dumps({"tags": ["test", "viz"]})
    )
    session.add(node)
    session.commit()

    # Retrieve and verify
    retrieved = session.query(VizMetadata).filter_by(node_id="test_node").first()
    assert retrieved is not None
    assert retrieved.node_id == "test_node"
    assert retrieved.role == "Tester"
    assert retrieved.description == "A node for testing purposes"
    
    # Verify JSON fields
    io_data = json.loads(retrieved.io_schema)
    assert io_data["input"] == "test_data"
    
    metrics_data = json.loads(retrieved.load_metrics)
    assert metrics_data["cognitive_load"] == 0.1

def test_viz_metadata_update(session):
    """Tests updating an existing metadata entry."""
    # Setup
    node = VizMetadata(
        node_id="update_node", 
        role="Initial Role", 
        description="Initial Desc", 
        code_mapping="initial", 
        io_schema="{}", 
        load_metrics="{}"
    )
    session.add(node)
    session.commit()

    # Update
    retrieved = session.query(VizMetadata).filter_by(node_id="update_node").first()
    retrieved.role = "Updated Role"
    retrieved.description = "Updated Description"
    session.commit()

    # Verify
    final = session.query(VizMetadata).filter_by(node_id="update_node").first()
    assert final.role == "Updated Role"
    assert final.description == "Updated Description"

def test_viz_metadata_delete(session):
    """Tests deleting a metadata entry."""
    # Setup
    node = VizMetadata(
        node_id="delete_node", 
        role="Delete Me", 
        description="Bye", 
        code_mapping="void", 
        io_schema="{}", 
        load_metrics="{}"
    )
    session.add(node)
    session.commit()

    # Delete
    retrieved = session.query(VizMetadata).filter_by(node_id="delete_node").first()
    session.delete(retrieved)
    session.commit()

    # Verify
    final = session.query(VizMetadata).filter_by(node_id="delete_node").first()
    assert final is None

def test_viz_metadata_unique_constraint(session):
    """Tests that node_id must be unique."""
    node1 = VizMetadata(
        node_id="unique_id", 
        role="R1", 
        description="D1", 
        code_mapping="C1", 
        io_schema="{}", 
        load_metrics="{}"
    )
    session.add(node1)
    session.commit()

    node2 = VizMetadata(
        node_id="unique_id", 
        role="R2", 
        description="D2", 
        code_mapping="C2", 
        io_schema="{}", 
        load_metrics="{}"
    )
    session.add(node2)
    
    with pytest.raises(IntegrityError):
        session.commit()
