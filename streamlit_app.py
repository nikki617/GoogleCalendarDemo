# streamlit_app.py

import streamlit as st
from llm_integration import get_tools, create_agent
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler

# Get tools and create the agent
tools = get_tools()
agent = create_agent(tools)

# Storing message history
msgs = StreamlitChatMessageHistory(key="special_app_key")

# Load the first AI message
if len(msgs.messages) == 0:
    msgs.add_ai_message("How may I assist you today?")

# Add the rest of the conversation
for msg in msgs.messages:
    if msg.type in ["ai", "human"]:
        st.chat_message(msg.type).write(msg.content)

# When the user enters a new prompt
if entered_prompt := st.chat_input("What does my day look like?"):
    # Add human message
    st.chat_message("human").write(entered_prompt)
    msgs.add_user_message(entered_prompt)

    # Get a response from the agent
    st_callback = StreamlitCallbackHandler(st.container())

    # Specify the default date range for the current week
    from_datetime = datetime.now()
    to_datetime = datetime.now() + timedelta(days=7)

    # Invoke the agent with the entered prompt and the date range
    response = agent.invoke({"input": entered_prompt, "from_datetime": from_datetime, "to_datetime": to_datetime}, {"callbacks": [st_callback]})

    # Add AI response
    response = response["output"]
    st.chat_message("ai").write(response)
    msgs.add_ai_message(response)
