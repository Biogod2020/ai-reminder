import chainlit as cl

@cl.on_chat_start
async def start():
    """Initializes the chat session and message history."""
    cl.user_session.set("message_history", [])
    await cl.Message(content="Welcome to the Universal Soul Console. How can I help you today?").send()

@cl.on_message
async def main(message: cl.Message):
    """Handles incoming user messages and visualizes the reasoning process."""
    message_history = cl.user_session.get("message_history")
    message_history.append({"role": "user", "content": message.content})

    async with cl.Step(name="Soul Reasoning") as step:
        step.input = message.content
        # Placeholder for AI logic
        step.output = "Thinking about task atomization and soul context..."

    msg = cl.Message(content=f"Received: {message.content}. Implementation pending.")
    await msg.send()
    
    message_history.append({"role": "assistant", "content": msg.content})
    cl.user_session.set("message_history", message_history)
