import os
import sys

# Ensure the project root is in the Python path
sys.path.append(os.getcwd())

import chainlit as cl
from core.orchestrator import SoulOrchestrator

@cl.on_chat_start
async def start():
    """Initializes the chat session, message history, and orchestrator."""
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
        step.output = f"Intent classified as: {result['intent']}"

    # Store current task title for callback
    cl.user_session.set("last_task_title", message.content)

    # If the agent has proposed actions (e.g. sub-tasks), show a confirmation card
    if result.get("proposed_actions"):
        actions = [
            cl.Action(name="approve_plan", value="approve", label="Approve Plan"),
            cl.Action(name="decline_plan", value="decline", label="Decline")
        ]
        
        content = f"### Proposed Plan for: {message.content}\n\n"
        for i, subtask in enumerate(result["proposed_actions"]):
            title = subtask.get("title", "Untitled")
            load = subtask.get("estimated_cognitive_load", "N/A")
            content += f"{i+1}. **{title}** (Load: {load})\n"
            if subtask.get("pro_tip"):
                content += f"   - *Pro-tip:* {subtask['pro_tip']}\n"
        
        await cl.Message(content=content, actions=actions).send()
    else:
        # Standard text response
        msg = cl.Message(content=result["response"])
        await msg.send()
        message_history.append({"role": "assistant", "content": msg.content})

    cl.user_session.set("message_history", message_history)

@cl.action_callback("approve_plan")
async def on_approve(action: cl.Action):
    """Callback for plan approval. Persists the plan to SQLite."""
    orchestrator = cl.user_session.get("orchestrator")
    task_title = cl.user_session.get("last_task_title")
    
    await orchestrator.approve_plan(task_title)
    
    await cl.Message(content=f"Plan for '{task_title}' approved and committed to your local database!").send()

@cl.action_callback("decline_plan")
async def on_decline(action: cl.Action):
    """Callback for plan rejection."""
    await cl.Message(content="Plan declined. Feel free to rephrase or give more specific instructions.").send()
