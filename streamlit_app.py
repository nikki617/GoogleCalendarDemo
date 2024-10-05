# streamlit_app.py

import streamlit as st
from calendar_integration import connect_calendar, get_events, add_event, GetEventArgs, AddEventArgs
from llm_integration import LangChainManager
from datetime import datetime, timedelta
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler  # Add this import
from langchain.callbacks.tracers import ConsoleCallbackHandler  # Make sure to import this too

def main():
    # Connect to Google Calendar
    calendar = connect_calendar()

    # Create an instance of LangChainManager
    langchain_manager = LangChainManager(st.secrets["openai"]["api_key"])

    # Define tools
    from langchain_core.tools import StructuredTool

    # Create GetEvents Tool
    list_event_tool = StructuredTool(
        name="GetEvents",
        func=lambda from_datetime, to_datetime: get_events(calendar, from_datetime, to_datetime),
        args_schema=GetEventArgs,
        description="Useful for getting the list of events from the user's calendar."
    )

    # Create AddEvent Tool
    add_event_tool = StructuredTool(
        name="AddEvent",
        func=lambda start_date_time, length_hours, event_name: add_event(calendar, start_date_time, length_hours, event_name),
        args_schema=AddEventArgs,
        description="Useful for adding an event with a start date, event name, and length in hours."
    )

    tools = [list_event_tool, add_event_tool]

    # Create the agent
    agent = langchain_manager.create_agent(tools)

    # Storing message history
    msgs = langchain_manager.load_message_history()

    # Load the first AI message
    if len(msgs.messages) == 0:
        msgs.add_ai_message("How may I assist you today?")

    # Add the rest of the conversation
    for msg in msgs.messages:
        if msg.type in ["ai", "human"]:
            st.chat_message(msg.type).write(msg.content)

    # When the user enters a new prompt
    if entered_prompt := st.chat_input("What does my day look like?"):
        st.chat_message("human").write(entered_prompt)
        msgs.add_user_message(entered_prompt)

        st_callback = StreamlitCallbackHandler(st.container())
        
        # Specify the default date range for the current week
        from_datetime = datetime.now()
        to_datetime = datetime.now() + timedelta(days=7)

        # Invoke the agent with the entered prompt and the date range
        response = agent.invoke(
            {"input": entered_prompt, "from_datetime": from_datetime, "to_datetime": to_datetime},
            {"callbacks": [st_callback, ConsoleCallbackHandler()]}
        )

        # Add AI response
        response = response["output"]
        st.chat_message("ai").write(response)
        msgs.add_ai_message(response)

if __name__ == "__main__":
    main()
