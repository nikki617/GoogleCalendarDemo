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
        current_year = datetime.now().year
        from_datetime = from_datetime.replace(year=current_year)
        to_datetime = to_datetime.replace(year=current_year)

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
        current_year = datetime.now().year
        start_date_time = start_date_time.replace(year=current_year)
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
        event_id: str = Field(description="ID of the event to reschedule")
        new_start_date_time: datetime = Field(description="new start date and time of event")
        new_length_hours: int = Field(description="new length of the event")

    def reschedule_event(event_id, new_start_date_time, new_length_hours):
        try:
            # Get the event by ID
            event = calendar.get_event(event_id=event_id, calendar_id="nikki617@bu.edu")
            # Update the start and end time
            event.start = new_start_date_time
            event.end = new_start_date_time + timedelta(hours=new_length_hours)
            # Update the event on Google Calendar
            calendar.update_event(event, calendar_id="nikki617@bu.edu")
            return f"Event {event_id} rescheduled successfully."
        except Exception as e:
            return f"Error rescheduling event: {str(e)}"

    reschedule_event_tool = StructuredTool(
        name="RescheduleEvent",
        func=reschedule_event,
        args_schema=RescheduleEventArgs,
        description="Useful for rescheduling an event by updating its start date and length."
    )

    # Event cancellation (delete) tool
    class CancelEventArgs(BaseModel):
        event_id: str = Field(description="ID of the event to cancel")

    def cancel_event(event_id):
        try:
            # Delete the event
            calendar.delete_event(event_id=event_id, calendar_id="nikki617@bu.edu")
            return f"Event {event_id} canceled successfully."
        except Exception as e:
            return f"Error canceling event: {str(e)}"

    cancel_event_tool = StructuredTool(
        name="CancelEvent",
        func=cancel_event,
        args_schema=CancelEventArgs,
        description="Useful for canceling (deleting) an event by its ID."
    )

    # Add all tools to the list
    tools = [
        list_event_tool, 
        add_event_tool, 
        reschedule_event_tool,  # Rescheduling tool
        cancel_event_tool       # Cancellation tool
    ]
    
    return tools, calendar
