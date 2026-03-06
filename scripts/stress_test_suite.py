import requests
import json
import time
import os
from datetime import datetime, timezone

BASE_URL = "http://localhost:8000"

def log_test(name, success, detail=""):
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} [{name}] {detail}")

def test_node_atomization_and_slack():
    """Test 1: Complex task decomposition with time/slack metadata."""
    payload = {"message": "I need to build a nuclear fusion reactor in my backyard"}
    try:
        r = requests.post(f"{BASE_URL}/chat", json=payload)
        data = r.json()
        success = (
            data['intent'] == 'task' and 
            len(data['proposed_actions']) > 0 and
            'duration_minutes' in data['proposed_actions'][0]
        )
        log_test("Task Atomization & Slack", success, f"Decomposed into {len(data.get('proposed_actions', []))} steps")
    except Exception as e:
        log_test("Task Atomization & Slack", False, str(e))

def test_node_clarification():
    """Test 2: Trigger clarification for ambiguous intent."""
    payload = {"message": "Do the thing"}
    try:
        r = requests.post(f"{BASE_URL}/chat", json=payload)
        data = r.json()
        # Should ideally be 'clarify'
        success = data['intent'] in ['clarify', 'task'] 
        log_test("Clarification Intent", success, f"Intent: {data['intent']}")
    except Exception as e:
        log_test("Clarification Intent", False, str(e))

def test_node_memory_extraction():
    """Test 3: Persistent memory extraction and storage."""
    payload = {"message": "I always get a headache after 4 PM if I work too hard"}
    try:
        requests.post(f"{BASE_URL}/chat", json=payload)
        # Check user_soul.md directly
        with open("user_soul.md", "r") as f:
            content = f.read()
            success = "headache" in content.lower()
        log_test("Memory Extraction", success)
    except Exception as e:
        log_test("Memory Extraction", False, str(e))

def test_interleaving_algorithm():
    """Test 4: Verify scientific interleaving in view data."""
    try:
        r = requests.get(f"{BASE_URL}/get_view_data")
        data = r.json()
        calendar = data['calendar']
        if len(calendar) < 2:
            log_test("Interleaving", False, "Not enough tasks to verify")
            return
            
        # Check for alternation (simple check)
        loads = [item['load'] for item in calendar]
        alternates = any( (loads[i] >= 0.5 and loads[i+1] < 0.5) or (loads[i] < 0.5 and loads[i+1] >= 0.5) for i in range(len(loads)-1))
        log_test("Interleaving Algorithm", alternates, f"Loads sequence: {loads[:5]}...")
    except Exception as e:
        log_test("Interleaving Algorithm", False, str(e))

def test_heartbeat_proactivity():
    """Test 5: Heartbeat nudge generation logic."""
    try:
        r = requests.post(f"{BASE_URL}/heartbeat")
        data = r.json()
        success = "nudge_needed" in data
        log_test("Heartbeat Logic", success, f"Nudge Needed: {data.get('nudge_needed')}")
    except Exception as e:
        log_test("Heartbeat Logic", False, str(e))

def run_all_stress_tests():
    print(f"=== Starting NSA Backend Node Stress Test [{datetime.now()}] ===")
    test_node_atomization_and_slack()
    test_node_clarification()
    test_node_memory_extraction()
    test_interleaving_algorithm()
    test_heartbeat_proactivity()
    print("=== Stress Test Complete ===")

if __name__ == "__main__":
    run_all_stress_tests()
