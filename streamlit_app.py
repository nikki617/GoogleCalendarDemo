import streamlit as st
from datetime import datetime, timedelta
from langchain_community.chat_message_histories import StreamlitChatMessageHistory

from llm_integration import create_llm_agent, invoke_agent

# Initialize message history
msgs = StreamlitChatMessageHistory(key="special_app_key")

# Load the first AI message
if len(msgs.messages) == 0:
    msgs.add_ai_message("How may I assist you today?")

# Add the rest of the conversation
for msg in msgs.messages:
    if msg.type in ["ai", "human"]:
        st.chat_message(msg.type).write(msg.content)

# Initialize the LLM agent
agent = create_llm_agent()

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

# New input for rescheduling events
if reschedule_prompt := st.chat_input("How would you like to reschedule an event?"):
    # Add human message for rescheduling
    st.chat_message("human").write(reschedule_prompt)
    msgs.add_user_message(reschedule_prompt)

    # Extract details from the reschedule prompt here (implement parsing logic)
    # Assuming you have parsed the values:
    # parsed_event_name, parsed_new_start_time, parsed_new_length_hours

    # Example parsing logic (you may need to customize this):
    # Let's assume user input format: "Reschedule Event: Test5 to October 10, 2023 at 3:00 PM for 2 hours"
    # You'll need to implement the parsing logic to extract these values
    parsed_event_name = "Test5"  # Example
    parsed_new_start_time = datetime(2023, 10, 10, 15, 0)  # Example
    parsed_new_length_hours = 2  # Example

    # Invoke the rescheduling function
    reschedule_response = invoke_agent(agent, f"Reschedule {parsed_event_name} to {parsed_new_start_time}", parsed_new_start_time, parsed_new_start_time + timedelta(hours=parsed_new_length_hours))

    # Add AI response for rescheduling
    st.chat_message("ai").write(reschedule_response)
    msgs.add_ai_message(reschedule_response)
