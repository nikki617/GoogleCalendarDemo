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
    class GetEventargs(BaseModel):
        from_datetime: datetime = Field(description="beginning of date range to retrieve events")
        to_datetime: datetime = Field(description="end of date range to retrieve events")

    def get_events(from_datetime, to_datetime):
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
        start = start_date_time
        end = start + timedelta(hours=length_hours)
        event = Event(event_name, start=start, end=end)
        return calendar.add_event(event, calendar_id="nikki617@bu.edu")

    add_event_tool = StructuredTool(
        name="AddEvent",
        func=add_event,
        args_schema=AddEventargs,
        description="Useful for adding an event with a start date, event name, and length in hours."
    )

    # Event rescheduling tool
    class RescheduleEventargs(BaseModel):
        event_id: str = Field(description="ID of the event to be rescheduled")
        new_start_datetime: datetime = Field(description="New start date and time for the event")
        new_length_hours: int = Field(description="New length of event in hours")

    def reschedule_event(event_id, new_start_datetime, new_length_hours):
        event = calendar.get_event(event_id, calendar_id="nikki617@bu.edu")
        if event:
            new_end = new_start_datetime + timedelta(hours=new_length_hours)
            event.start = new_start_datetime
            event.end = new_end
            calendar.update_event(event, calendar_id="nikki617@bu.edu")
            return f"Event '{event.summary}' rescheduled to {new_start_datetime}"
        return f"Event with ID {event_id} not found."

    reschedule_event_tool = StructuredTool(
        name="RescheduleEvent",
        func=reschedule_event,
        args_schema=RescheduleEventargs,
        description="Useful for rescheduling an event with a new start date, time, and length."
    )

    # Event cancelling tool
    class CancelEventargs(BaseModel):
        event_id: str = Field(description="ID of the event to cancel")

    def cancel_event(event_id):
        event = calendar.get_event(event_id, calendar_id="nikki617@bu.edu")
        if event:
            calendar.delete_event(event, calendar_id="nikki617@bu.edu")
            return f"Event '{event.summary}' has been canceled."
        return f"Event with ID {event_id} not found."

    cancel_event_tool = StructuredTool(
        name="CancelEvent",
        func=cancel_event,
        args_schema=CancelEventargs,
        description="Useful for canceling an event by providing its event ID."
    )

    # Add all tools to a list
    tools = [list_event_tool, add_event_tool, reschedule_event_tool, cancel_event_tool]
    
    return tools, calendar
