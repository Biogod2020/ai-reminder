import pytest
import os
from core.memory import SoulMemory

@pytest.mark.asyncio
async def test_soul_memory_add_and_search():
    # Use a temporary directory for local memory storage if possible
    memory = SoulMemory()
    
    # Add a fact
    await memory.add_fact("The user likes to work on deep research in the morning.", user_id="test_user")
    
    # Search for related facts
    results = await memory.search_facts("What are the user's morning habits?", user_id="test_user")
    
    assert any("morning" in r['content'].lower() for r in results)

@pytest.mark.asyncio
async def test_soul_memory_sync_to_file(tmp_path):
    # Test if memory updates can be reflected/synced to our user_soul.md
    soul_file = tmp_path / "user_soul.md"
    memory = SoulMemory(soul_file_path=str(soul_file))
    
    await memory.add_fact("I am going on a trip this Thursday.", user_id="test_user")
    
    # For MVP, we might just verify the file was touched or updated
    assert os.path.exists(soul_file)
    with open(soul_file, "r") as f:
        content = f.read()
        assert "Thursday" in content
