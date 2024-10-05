# Required Imports
from gcsa.event import Event
from gcsa.google_calendar import GoogleCalendar
from gcsa.recurrence import Recurrence, DAILY, SU, SA
from google.oauth2 import service_account
from beautiful_date import Jan, Apr, Sept, Oct
import json
import os
from datetime import date, datetime, timedelta
from beautiful_date import hours
from langchain_core.runnables.utils import ConfigurableFieldSpec
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents.react.agent import create_react_agent
from langchain_core.output_parsers import StrOutputParser
from langchain_core.tools import Tool, StructuredTool
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.agents import AgentType
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI
from langchain.callbacks.tracers import ConsoleCallbackHandler
from pydantic import BaseModel, Field
import streamlit as st

# Google Calendar Credentials
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["CalendarAPI"],
    scopes=["https://www.googleapis.com/auth/calendar"]
)

# Create the GoogleCalendar instance
calendar = GoogleCalendar(credentials=credentials)

# Event listing tool
class GetEventargs(BaseModel):
    from_datetime: datetime = Field(description="beginning of date range to retrieve events")
    to_datetime: datetime = Field(description="end of date range to retrieve events")

def get_events(from_datetime, to_datetime):
    current_year = datetime.now().year
    from_datetime = from_datetime.replace(year=current_year)
    to_datetime = to_datetime.replace(year=current_year)
    
    events = calendar.get_events(calendar_id="nikki617@bu.edu", time_min=from_datetime, time_max=to_datetime)
    return list(events)

list_event_tool = StructuredTool(
    name="GetEvents",
    func=get_events,
    args_schema=GetEventargs,
    description="Useful for getting the list of events from the user's calendar."
)

# Event adding tool
class AddEventargs(BaseModel):
    start_date_time: datetime = Field(description="start date and time of event")
    length_hours: int = Field(description="length of event")
    event_name: str = Field(description="name of the event")

def add_event(start_date_time, length_hours, event_name):
    current_year = datetime.now().year
    start_date_time = start_date_time.replace(year=current_year)
    start = start_date_time
    end = start + length_hours * hours
    event = Event(event_name, start=start, end=end)
    return calendar.add_event(event, calendar_id="nikki617@bu.edu")

add_event_tool = StructuredTool(
    name="AddEvent",
    func=add_event,
    args_schema=AddEventargs,
    description="Useful for adding an event with a start date, event name, and length in hours."
)

tools = [list_event_tool, add_event_tool]

# Create the LLM
llm = ChatOpenAI(api_key=st.secrets["openai"]["api_key"], temperature=0.1)

# Chatbot prompt
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful Google Calendar assistant"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
)

# Create the agent
agent = create_tool_calling_agent(llm, tools, prompt)
agent = AgentExecutor(
    agent=agent, 
    tools=tools,
)

# Storing message history
msgs = StreamlitChatMessageHistory(key="special_app_key")

# Streamlit app layout
st.set_page_config(page_title="Google Calendar Assistant", layout="wide")
# Removed the title to clean up UI
# st.title("Google Calendar Assistant")
st.markdown(
    """
    <style>
    .sidebar .sidebar-content {
        padding: 1rem;
    }
    .chat-message {
        padding: 10px;
        border-radius: 5px;
    }
    .human {
        background-color: #d1e7dd;
        margin-bottom: 5px;
    }
    .ai {
        background-color: #f8d7da;
        margin-bottom: 5px;
    }
    </style>
    """, unsafe_allow_html=True
)

# Layout for chat and calendar
col1, col2 = st.columns([1, 2])

# Left side for chat messages
with col1:
    st.sidebar.title("Chat")

    # User input for the chat
    if entered_prompt := st.sidebar.text_input("What does my day look like?", placeholder="Ask me about your schedule!"):
        # Clear the message history for the new prompt
        msgs.clear()

        st.sidebar.chat_message("human").write(entered_prompt)
        msgs.add_user_message(entered_prompt)

        # Get a response from the agent
        st_callback = StreamlitCallbackHandler(st.container())
        
        # Specify the default date range for the current week
        from_datetime = datetime.now()
        to_datetime = datetime.now() + timedelta(days=7)
        
        # Invoke the agent, but do not display the response yet
        response = agent.invoke({"input": entered_prompt, "from_datetime": from_datetime, "to_datetime": to_datetime}, {"callbacks": [st_callback, ConsoleCallbackHandler()]})

        # Check if the response contains output and log it if necessary
        if 'output' in response:
            response_output = response["output"]
            # Log the response to a file instead of displaying it
            with open('log.txt', 'a') as log_file:
                log_file.write(f"User: {entered_prompt}\nAgent: {response_output}\n")

            # Optionally display a message in the sidebar
            st.sidebar.chat_message("ai").write("Response generated. Check logs for details.")
            msgs.add_ai_message("Response generated. Check logs for details.")

# Right side for calendar
with col2:
    st.subheader("Your Calendar")
    calendar_embed_code = """
    <iframe src="https://calendar.google.com/calendar/embed?src=nikki617%40bu.edu&ctz=Europe%2FBerlin" 
            style="border: 0" width="100%" height="650" frameborder="0" scrolling="no"></iframe>
    """
    st.components.v1.html(calendar_embed_code, height=650)
