import streamlit as st
from google.oauth2 import service_account
from llm_integration import agent, msgs  # Assuming agent and message storage is defined here
from calendar_integration import tools  # Assuming tools are defined here

# Google Calendar Setup (ensure this is in the main app)
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["CalendarAPI"],
    scopes=["https://www.googleapis.com/auth/calendar"]
)

# Initialize Streamlit chat
if len(msgs.messages) == 0:
    msgs.add_ai_message("How may I assist you today?")

for msg in msgs.messages:
    if msg.type in ["ai", "human"]:
        st.chat_message(msg.type).write(msg.content)

# User input
if entered_prompt := st.chat_input("What does my day look like?"):
    st.chat_message("human").write(entered_prompt)
    msgs.add_user_message(entered_prompt)

    # Call the agent
    response = agent.invoke({"input": entered_prompt})  # Add date range as needed
    st.chat_message("ai").write(response["output"])
    msgs.add_ai_message(response["output"])
