import streamlit as st
from datetime import datetime, timedelta
from langchain_community.chat_message_histories import StreamlitChatMessageHistory

from llm_integration import create_llm_agent, invoke_agent
from calendar_integration import get_events, add_event, cancel_event, GetEventargs, AddEventargs, CancelEventargs

# Initialize message history
msgs = StreamlitChatMessageHistory(key="special_app_key")

# Load the first AI message
if len(msgs.messages) == 0:
    msgs.add_ai_message("How may I assist you today?")

# Initialize the LLM agent
agent = create_llm_agent()

# Define the layout for the app
col1, col2 = st.columns([1, 2])  # 1: Calendar Column, 2: Chat Column

# Calendar Column
with col1:
    st.header("Google Calendar")
    # Embed Google Calendar using iframe
    calendar_id = "nikki617@bu.edu"  # Your calendar ID
    timezone = "America/New_York"  # Set your timezone
    iframe_code = f'<iframe src="https://calendar.google.com/calendar/embed?src={calendar_id}&ctz={timezone}" style="border: 0" width="400" height="600" frameborder="0" scrolling="no"></iframe>'
    
    # Render the iframe
    st.markdown(iframe_code, unsafe_allow_html=True)

# Chat Column
with col2:
    # Add the rest of the conversation
    for msg in msgs.messages:
        if msg.type in ["ai", "human"]:
            st.chat_message(msg.type).write(msg.content)

    # When the user enters a new prompt
    if entered_prompt := st.chat_input("What does my day look like?"):
        # Add human message
        st.chat_message("human").write(entered_prompt)
        msgs.add_user_message(entered_prompt)

        # Specify the default date range for the current week
        from_datetime = datetime.now()
        to_datetime = datetime.now() + timedelta(days=7)

        # Get a response from the agent
        response = invoke_agent(agent, entered_prompt, from_datetime, to_datetime)

        # Add AI response
        st.chat_message("ai").write(response)
        msgs.add_ai_message(response)
