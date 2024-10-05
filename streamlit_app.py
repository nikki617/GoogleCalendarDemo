# gcsa imports
from gcsa.event import Event
from gcsa.google_calendar import GoogleCalendar
from google.oauth2 import service_account

# misc imports
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.agents import StructuredTool
from langchain_openai import ChatOpenAI
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler
import streamlit as st
import json
from datetime import datetime

# Connecting to the Google Calendar through an API
# Load Google Calendar credentials from Streamlit secrets
google_calendar_credentials = {
    "type": st.secrets["CalendarAPI"]["type"],
    "project_id": st.secrets["CalendarAPI"]["project_id"],
    "private_key_id": st.secrets["CalendarAPI"]["private_key_id"],
    "private_key": st.secrets["CalendarAPI"]["private_key"].replace("\\n", "\n"),
    "client_email": st.secrets["CalendarAPI"]["client_email"],
    "client_id": st.secrets["CalendarAPI"]["client_id"],
    "auth_uri": st.secrets["CalendarAPI"]["auth_uri"],
    "token_uri": st.secrets["CalendarAPI"]["token_uri"],
    "auth_provider_x509_cert_url": st.secrets["CalendarAPI"]["auth_provider_x509_cert_url"],
    "client_x509_cert_url": st.secrets["CalendarAPI"]["client_x509_cert_url"],
}

credentials = service_account.Credentials.from_service_account_info(
    google_calendar_credentials,
    scopes=["https://www.googleapis.com/auth/calendar"]
)

# Create the Google Calendar instance
calendar = GoogleCalendar(credentials=credentials)

# Event listing tool
class GetEventargs(BaseModel):
    from_datetime: datetime = Field(description="beginning of date range to retrieve events")
    to_datetime: datetime = Field(description="end of date range to retrieve events")

def get_events(from_datetime, to_datetime):
    events = calendar.get_events(calendar_id="mndhamod@gmail.com", time_min=from_datetime, time_max=to_datetime)
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
    length_hours: int = Field(description="length of event in hours")
    event_name: str = Field(description="name of the event")

def add_event(start_date_time, length_hours, event_name):
    start = start_date_time
    end = start + length_hours * 3600  # Convert hours to seconds
    event = Event(event_name, start=start, end=end)
    return calendar.add_event(event, calendar_id="mndhamod@gmail.com")

add_event_tool = StructuredTool(
    name="AddEvent",
    func=add_event,
    args_schema=AddEventargs,
    description="Useful for adding an event with a start date, event name, and length in hours."
)

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

# Create the agent that will integrate the provided calendar tool with the LLM
agent = create_tool_calling_agent(llm, [list_event_tool, add_event_tool], prompt)
agent = AgentExecutor(agent=agent, tools=[list_event_tool, add_event_tool])

# Storing message history
msgs = StreamlitChatMessageHistory(key="special_app_key")

# Load the first AI message
if len(msgs.messages) == 0:
    msgs.add_ai_message("How may I assist you today?")

# Add the rest of the conversation
for msg in msgs.messages:
    if (msg.type in ["ai", "human"]):
        st.chat_message(msg.type).write(msg.content)

# When the user enters a new prompt
if entered_prompt := st.chat_input("What does my day look like?"):
    st.chat_message("human").write(entered_prompt)
    msgs.add_user_message(entered_prompt)

    # Get a response from the agent
    st_callback = StreamlitCallbackHandler(st.container())
    response = agent.invoke({"input": entered_prompt}, {"callbacks": [st_callback]})

    # Add AI response
    response = response["output"]
    st.chat_message("ai").write(response)
    msgs.add_ai_message(response)
