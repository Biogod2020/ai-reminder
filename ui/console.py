import os
import sys

# Ensure the project root is in the Python path
sys.path.append(os.getcwd())

import chainlit as cl
from core.orchestrator import SoulOrchestrator

@cl.on_chat_start
async def start():
    """Initializes the chat session and message history."""
    cl.user_session.set("message_history", [])
    cl.user_session.set("orchestrator", SoulOrchestrator())
    await cl.Message(content="Welcome to the Universal Soul Console. How can I help you today?").send()

@cl.on_message
async def main(message: cl.Message):
    """Handles incoming user messages and visualizes the reasoning process."""
    message_history = cl.user_session.get("message_history")
    orchestrator = cl.user_session.get("orchestrator")
    
    message_history.append({"role": "user", "content": message.content})

    async with cl.Step(name="Soul Reasoning") as step:
        step.input = message.content
        # Execute the orchestrator
        result = await orchestrator.run(message.content, history=message_history)
        step.output = f"Intent classified as: {result['intent']}\nResponse: {result['response']}"

    msg = cl.Message(content=result["response"])
    await msg.send()
    
    message_history.append({"role": "assistant", "content": msg.content})
    cl.user_session.set("message_history", message_history)
