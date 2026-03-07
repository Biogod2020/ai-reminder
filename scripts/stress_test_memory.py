import asyncio
import os
import sys
import time
import logging
import random
from typing import List

# Ensure project root is in path
sys.path.append(os.getcwd())

from core.memory import SharedMemoryManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("StressTest")

async def stress_test_volume(manager: SharedMemoryManager, count: int = 5):
    """Tests volume memory ingestion SEQUENTIALLY to debug hangs."""
    logger.info(f"Starting Volume Test (Sequential): {count} entries")
    start_time = time.time()
    
    for i in range(count):
        content = f"Fact {i}: User prefers {random.choice(['Python', 'Rust', 'Go'])}."
        logger.info(f"Adding fact {i}...")
        try:
            await manager.add(content, user_id="stress_user", metadata={"scope": "stress"})
            logger.info(f"Fact {i} added.")
        except Exception as e:
            logger.error(f"Failed to add fact {i}: {e}")
    
    duration = time.time() - start_time
    logger.info(f"Volume Test Complete. Duration: {duration:.2f}s")
    return duration

async def stress_test_retrieval(manager: SharedMemoryManager, queries: int = 3):
    """Tests retrieval performance SEQUENTIALLY."""
    logger.info(f"Starting Retrieval Test (Sequential): {queries} searches")
    start_time = time.time()
    
    for i in range(queries):
        query = f"What language does the user prefer?"
        logger.info(f"Searching {i}...")
        try:
            results = await manager.search(query, user_id="stress_user", scope="stress")
            logger.info(f"Search {i} found {len(results)} results.")
        except Exception as e:
            logger.error(f"Search {i} failed: {e}")
    
    duration = time.time() - start_time
    logger.info(f"Retrieval Test Complete. Duration: {duration:.2f}s")
    return duration

async def main():
    manager = SharedMemoryManager()
    
    print("\n--- 🚀 Starting Sequential Memory Engine Test ---")
    
    # 1. Volume Ingestion
    await stress_test_volume(manager, 5) 
    
    # 2. Retrieval Speed
    await stress_test_retrieval(manager, 3)
    
    print("--- Test Finished ---")

if __name__ == "__main__":
    asyncio.run(main())
