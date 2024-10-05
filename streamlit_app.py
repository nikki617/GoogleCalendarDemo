# gcsa imports
from gcsa.event import Event
from gcsa.google_calendar import GoogleCalendar
from google.oauth2 import service_account

# misc imports
from beautiful_date import hours
from datetime import datetime, timedelta

# langchain imports
from langchain_core.tools import StructuredTool
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler
from pydantic import BaseModel, Field

import streamlit as st

##-------------------
## Connecting to the Google Calendar through an API

# Get the credentials from Secrets.
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["CalendarAPI"],
    scopes=["https://www.googleapis.com/auth/calendar"]
)

# Create the GoogleCalendar.
calendar = GoogleCalendar(credentials=credentials)

#------- 
### Event listing tool

# Parameters needed to look for an event
class GetEventargs(BaseModel):
    from_datetime: datetime = Field(description="beginning of date range to retrieve events")
    to_datetime: datetime = Field(description="end of date range to retrieve events")

# Define the tool 
def get_events(from_datetime: datetime, to_datetime: datetime):
    events = calendar.get_events(calendar_id="nikki617@bu.edu", time_min=from_datetime, time_max=to_datetime)
    return list(events)

# Create a Tool object 
list_event_tool = StructuredTool(
    name="GetEvents",
    func=get_events,
    args_schema=GetEventargs,  # Ensure this is a Pydantic model
    description="Useful for getting the list of events from the user's calendar."
)

#------------

### Event adding tool

# Parameters needed to add an event
class AddEventargs(BaseModel):
    start_date_time: datetime = Field(description="start date and time of event")
    length_hours: int = Field(description="length of event")
    event_name: str = Field(description="name of the event")

# Define the tool 
def add_event(start_date_time: datetime, length_hours: int, event_name: str):
    start = start_date_time
    end = start + timedelta(hours=length_hours)
    event = Event(event_name, start=start, end=end)
    return calendar.add_event(event, calendar_id="nikki617@bu.edu")

# Create a Tool object 
add_event_tool = StructuredTool(
    name="AddEvent",
    func=add_event,
    args_schema=AddEventargs,  # Ensure this is a Pydantic model
    description="Useful for adding an event with a start date, event name, and length in hours."
)

#------------

## Update this list with the new tools
tools = [list_event_tool, add_event_tool]

#-----------

# Create the LLM
llm = ChatOpenAI(api_key=st.secrets["openai"]["api_key"], temperature=0.1)

# Messages used by the chatbot
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful Google Calendar assistant"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
)

# Creating the agent that will integrate the provided calendar tool with the LLM.
agent = create_tool_calling_agent(llm, tools, prompt)
agent = AgentExecutor(
    agent=agent, 
    tools=tools,
)

#--------------------

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
    # Get the current date for the range
    current_date = datetime.now()
    start_of_month = current_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    end_of_month = (start_of_month + timedelta(days=30)).replace(day=1)  # Next month

    # Prepare to get events
    event_args = GetEventargs(from_datetime=start_of_month, to_datetime=end_of_month)

    # Add human message
    st.chat_message("human").write(entered_prompt)
    msgs.add_user_message(entered_prompt)

    # Get a response from the agent
    st_callback = StreamlitCallbackHandler(st.container())
    response = agent.invoke({"input": entered_prompt}, {"callbacks": [st_callback]})

    # Add AI response.
    response = response["output"]
    st.chat_message("ai").write(response)
    msgs.add_ai_message(response)
