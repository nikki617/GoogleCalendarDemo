import streamlit as st
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
import pandas as pd

# Connect to Google Calendar through an API
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["CalendarAPI"],
    scopes=["https://www.googleapis.com/auth/calendar"]
)

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

# Update this list with the new tools
tools = [list_event_tool, add_event_tool]

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

# Storing message history
msgs = StreamlitChatMessageHistory(key="special_app_key")

# Layout with chat on the left and calendar on the right
col1, col2 = st.columns([2, 1])  # Adjust the ratios as needed

# Chat Interface
with col1:
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
        response = agent.invoke({"input": entered_prompt, "from_datetime": from_datetime, "to_datetime": to_datetime}, {"callbacks": [st_callback, ConsoleCallbackHandler()]})

        # Add AI response
        response = response["output"]
        st.chat_message("ai").write(response)
        msgs.add_ai_message(response)

# Calendar Interface
with col2:
    st.subheader("Your Calendar")
    
    # Create a DataFrame for the calendar
    now = datetime.now()
    month = now.month
    year = now.year
    
    # Get events for the current month
    start_date = datetime(year, month, 1)
    end_date = (start_date + pd.DateOffset(months=1)).replace(day=1)
    events = get_events(start_date, end_date)

    # Create a dictionary to hold events by day
    events_by_day = {}
    for event in events:
        event_day = event.start.day
        events_by_day[event_day] = event.summary

    # Create the calendar grid
    days_in_month = (end_date - start_date).days
    start_weekday = start_date.weekday()  # Monday is 0
    calendar_grid = [["" for _ in range(7)] for _ in range(6)]  # 6 rows for max 6 weeks

    # Fill the calendar grid
    day = 1
    for week in range(6):
        for weekday in range(7):
            if week == 0 and weekday < start_weekday:
                calendar_grid[week][weekday] = ""
            elif day <= days_in_month:
                calendar_grid[week][weekday] = day
                day += 1

    # Display the calendar
    st.markdown("<style>table {width: 100%; text-align: center;}</style>", unsafe_allow_html=True)
    st.write("<table>", unsafe_allow_html=True)
    st.write("<tr><th>Sun</th><th>Mon</th><th>Tue</th><th>Wed</th><th>Thu</th><th>Fri</th><th>Sat</th></tr>", unsafe_allow_html=True)

    for week in calendar_grid:
        st.write("<tr>", unsafe_allow_html=True)
        for day in week:
            if day != "":
                event_name = events_by_day.get(day, "")
                st.write(f"<td style='background-color: lightgreen;'>" + str(day) + ("<br>" + event_name if event_name else "") + "</td>", unsafe_allow_html=True)
            else:
                st.write("<td></td>", unsafe_allow_html=True)
        st.write("</tr>", unsafe_allow_html=True)
    
    st.write("</table>", unsafe_allow_html=True)
