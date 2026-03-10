import pytest
import os
import shutil
import logging
from core.memory import SharedMemoryManager

# Configure logging to see output during tests
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("TestMemory")

@pytest.fixture(scope="module")
def setup_memory():
    logger.info("Setting up setup_memory fixture...")
    # Setup a temporary memory directory for tests
    test_db_path = ".test_mem0_db"
    if os.path.exists(test_db_path):
        logger.info(f"Removing existing test db at {test_db_path}")
        shutil.rmtree(test_db_path)
    
    # Initialize SharedMemoryManager with test path
    manager = SharedMemoryManager(db_path=test_db_path)
    logger.info("SharedMemoryManager initialized for testing.")
    yield manager
    
    # Cleanup
    if os.path.exists(test_db_path):
        logger.info(f"Cleaning up test db at {test_db_path}")
        shutil.rmtree(test_db_path)

@pytest.mark.asyncio
async def test_singleton():
    logger.info("Running test_singleton...")
    manager1 = SharedMemoryManager()
    manager2 = SharedMemoryManager()
    assert manager1 is manager2
    logger.info("test_singleton passed.")

@pytest.mark.asyncio
async def test_add_and_search_memory(setup_memory):
    logger.info("Running test_add_and_search_memory...")
    manager = setup_memory
    user_id = "test_user"
    
    # Add a memory
    logger.info("Calling manager.add...")
    await manager.add("I prefer working in the mornings", user_id=user_id, metadata={"scope": "soul"})
    logger.info("manager.add completed.")
    
    # Search for the memory
    logger.info("Calling manager.search...")
    results = await manager.search("When does the user prefer working?", user_id=user_id)
    logger.info(f"manager.search completed. Found {len(results)} results.")
    
    assert len(results) > 0
    assert "mornings" in results[0]["content"].lower()
    logger.info("test_add_and_search_memory passed.")

@pytest.mark.asyncio
async def test_hierarchical_memory(setup_memory):
    logger.info("Running test_hierarchical_memory...")
    manager = setup_memory
    user_id = "test_user"
    
    # Add short-term memory
    logger.info("Calling manager.add for session scope...")
    await manager.add("Currently working on memory module", user_id=user_id, metadata={"scope": "session"})
    logger.info("manager.add for session scope completed.")
    
    # Search specifically for session scope
    logger.info("Searching for session scope...")
    results = await manager.search("What is the current task?", user_id=user_id, scope="session")
    logger.info(f"Session search found {len(results)} results.")
    assert any("memory module" in r["content"].lower() for r in results)
    
    # Search for long-term soul scope
    logger.info("Searching for soul scope...")
    results = await manager.search("What is the current task?", user_id=user_id, scope="soul")
    logger.info(f"Soul search found {len(results)} results.")
    # Should not find the session memory if filtering works
    assert not any("memory module" in r["content"].lower() for r in results)
    logger.info("test_hierarchical_memory passed.")
