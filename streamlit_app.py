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

# When the user enters a new prompt for rescheduling
if entered_prompt := st.chat_input("What event would you like to reschedule?"):
    # Add human message
    st.chat_message("human").write(entered_prompt)
    msgs.add_user_message(entered_prompt)

    # Example: Parse the prompt to extract the event name, new date/time, and length
    try:
        # Example parsing logic (you can replace this with more robust parsing)
        parts = entered_prompt.split(" to ")
        event_name = parts[0].replace("Reschedule ", "").strip()
        new_start_time_str, length_str = parts[1].split(" for ")
        new_start_datetime = datetime.strptime(new_start_time_str.strip(), "%Y-%m-%d %H:%M")
        length_hours = int(length_str.replace(" hours", "").strip())

        # Call the reschedule_event function
        response = invoke_agent(agent, event_name, new_start_datetime, length_hours)

        # Add AI response
        st.chat_message("ai").write(response)
        msgs.add_ai_message(response)

    except Exception as e:
        st.chat_message("ai").write(f"Error processing your request: {str(e)}")
