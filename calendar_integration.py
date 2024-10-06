# calendar_integration.py
from gcsa.event import Event
from gcsa.google_calendar import GoogleCalendar
from google.oauth2 import service_account
from pydantic import BaseModel, Field
from datetime import datetime
from langchain_core.tools import StructuredTool  # Import StructuredTool
import streamlit as st

# Google Calendar Credentials
def setup_google_calendar_tools():
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
        end = start + length_hours * 60 * 60  # Assuming hours are in seconds
        event = Event(event_name, start=start, end=end)
        return calendar.add_event(event, calendar_id="nikki617@bu.edu")

    add_event_tool = StructuredTool(
        name="AddEvent",
        func=add_event,
        args_schema=AddEventargs,
        description="Useful for adding an event with a start date, event name, and length in hours."
    )

    tools = [list_event_tool, add_event_tool]

    return tools, calendar
