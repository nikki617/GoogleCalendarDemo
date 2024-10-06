# calendar_integration.py
from gcsa.event import Event
from gcsa.google_calendar import GoogleCalendar
from google.oauth2 import service_account
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from langchain_core.tools import StructuredTool
import streamlit as st

def setup_google_calendar_tools():
    # Google Calendar Credentials
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["CalendarAPI"],
        scopes=["https://www.googleapis.com/auth/calendar"]
    )

    # Create the GoogleCalendar instance
    calendar = GoogleCalendar(credentials=credentials)

    # Event listing tool
    class GetEventArgs(BaseModel):
        from_datetime: datetime = Field(description="beginning of date range to retrieve events")
        to_datetime: datetime = Field(description="end of date range to retrieve events")

    def get_events(from_datetime, to_datetime):
        events = calendar.get_events(calendar_id="nikki617@bu.edu", time_min=from_datetime, time_max=to_datetime)
        return list(events)

    list_event_tool = StructuredTool(
        name="GetEvents",
        func=get_events,
        args_schema=GetEventArgs,
        description="Useful for getting the list of events from the user's calendar."
    )

    # Event adding tool
    class AddEventArgs(BaseModel):
        start_date_time: datetime = Field(description="start date and time of event")
        length_hours: int = Field(description="length of event")
        event_name: str = Field(description="name of the event")

    def add_event(start_date_time, length_hours, event_name):
        start = start_date_time
        end = start + timedelta(hours=length_hours)
        event = Event(event_name, start=start, end=end)
        return calendar.add_event(event, calendar_id="nikki617@bu.edu")

    add_event_tool = StructuredTool(
        name="AddEvent",
        func=add_event,
        args_schema=AddEventArgs,
        description="Useful for adding an event with a start date, event name, and length in hours."
    )

    # Event rescheduling tool
    class RescheduleEventArgs(BaseModel):
        event_id: str = Field(description="ID of the event to be rescheduled")
        new_start_date_time: datetime = Field(description="new start date and time of the event")
        new_length_hours: int = Field(description="new length of event")

    def reschedule_event(event_id, new_start_date_time, new_length_hours):
        event = calendar.get_event(event_id=event_id)
        event.start = new_start_date_time
        event.end = new_start_date_time + timedelta(hours=new_length_hours)
        return calendar.update_event(event)

    reschedule_event_tool = StructuredTool(
        name="RescheduleEvent",
        func=reschedule_event,
        args_schema=RescheduleEventArgs,
        description="Useful for rescheduling an event by its ID with a new start time and duration."
    )

    # Event canceling tool
    class CancelEventArgs(BaseModel):
        event_id: str = Field(description="ID of the event to be canceled")

    def cancel_event(event_id):
        return calendar.delete_event(event_id=event_id)

    cancel_event_tool = StructuredTool(
        name="CancelEvent",
        func=cancel_event,
        args_schema=CancelEventArgs,
        description="Useful for canceling an event by its ID."
    )

    tools = [list_event_tool, add_event_tool, reschedule_event_tool, cancel_event_tool]
    return tools, calendar
