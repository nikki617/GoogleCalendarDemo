# streamlit_app.py

import streamlit as st
from datetime import datetime, timedelta
from llm_integration import create_agent
from beautiful_date import hours

# Initialize the agent
agent = create_agent()

# Storing message history
msgs = st.session_state.get("chat_history", [])
if not msgs:
    msgs.append({"type": "ai", "content": "How may I assist you today?"})

# Load the conversation
for msg in msgs:
    st.chat_message(msg["type"]).write(msg["content"])

# When the user enters a new prompt
if entered_prompt := st.chat_input("What does my day look like?"):
    # Add human message
    st.chat_message("human").write(entered_prompt)
    msgs.append({"type": "human", "content": entered_prompt})

    # Specify the default date range for the current week
    from_datetime = datetime.now()
    to_datetime = datetime.now() + timedelta(days=7)

    # Invoke the agent with the entered prompt and the date range
    response = agent.invoke({"input": entered_prompt, "from_datetime": from_datetime, "to_datetime": to_datetime})

    # Add AI response
    response = response["output"]
    st.chat_message("ai").write(response)
    msgs.append({"type": "ai", "content": response})

    # Store the updated message history in session state
    st.session_state.chat_history = msgs
