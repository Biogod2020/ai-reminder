import os

def test_console_file_exists():
    assert os.path.exists("ui/console.py")

def test_console_has_chainlit_imports():
    with open("ui/console.py", "r") as f:
        content = f.read()
        assert "import chainlit as cl" in content
        assert "@cl.on_chat_start" in content
        assert "@cl.on_message" in content
