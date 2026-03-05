import os

def test_clt_hci_exists():
    assert os.path.exists('research/papers/clt_hci.md')

def test_circadian_habits_exists():
    assert os.path.exists('research/papers/circadian_habits.md')

def test_agentic_ai_exists():
    assert os.path.exists('research/papers/agentic_ai.md')

def test_infantagent_source_exists():
    assert os.path.exists('research/sources/infantagent_next.md')

def test_clt_source_exists():
    assert os.path.exists('research/sources/cognitive_load_traces.md')
