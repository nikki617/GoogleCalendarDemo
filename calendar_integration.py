from gcsa.event import Event
from gcsa.google_calendar import GoogleCalendar
from google.oauth2 import service_account
from datetime import datetime
from pydantic import BaseModel, Field
from beautiful_date import hours
import streamlit as st

# Connect to Google Calendar using the credentials from Streamlit secrets
def get_calendar():
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["CalendarAPI"],
        scopes=["https://www.googleapis.com/auth/calendar"]
    )
    return GoogleCalendar(credentials=credentials)

calendar = get_calendar()

# Parameters needed to look for an event
class GetEventargs(BaseModel):
    from_datetime: datetime = Field(description="beginning of date range to retrieve events")
    to_datetime: datetime = Field(description="end of date range to retrieve events")

# Define the function to retrieve events
def get_events(from_datetime, to_datetime):
    current_year = datetime.now().year
    from_datetime = from_datetime.replace(year=current_year)
    to_datetime = to_datetime.replace(year=current_year)

    events = calendar.get_events(calendar_id="nikki617@bu.edu", time_min=from_datetime, time_max=to_datetime)
    return list(events)

# Parameters needed to add an event
class AddEventargs(BaseModel):
    start_date_time: datetime = Field(description="start date and time of event")
    length_hours: int = Field(description="length of event")
    event_name: str = Field(description="name of the event")

# Define the function to add an event
def add_event(start_date_time, length_hours, event_name):
    current_year = datetime.now().year
    start_date_time = start_date_time.replace(year=current_year)
    start = start_date_time
    end = start + length_hours * hours
    event = Event(event_name, start=start, end=end)
    return calendar.add_event(event, calendar_id="nikki617@bu.edu")

# Parameters needed to cancel an event
class CancelEventargs(BaseModel):
    event_name: str = Field(description="name of the event to be canceled")
    from_datetime: datetime = Field(description="beginning of the date range to search for events to cancel")
    to_datetime: datetime = Field(description="end of the date range to search for events to cancel")

def cancel_event(event_name: str, from_datetime: datetime, to_datetime: datetime):
    # Retrieve events in the given date range
    events = calendar.get_events(calendar_id="nikki617@bu.edu", time_min=from_datetime, time_max=to_datetime)

    # Debug: Print out the retrieved events for verification
    print("Retrieved Events:")
    for event in events:
        print(f"- {event.summary} at {event.start} to {event.end}")

    # Look for the event with the matching name
    for event in events:
        if event.summary == event_name:
            # If found, delete the event
            calendar.delete_event(event, calendar_id="nikki617@bu.edu")
            return f"Event '{event_name}' has been canceled."

    return f"No event named '{event_name}' was found in the given date range."

# Parameters needed to reschedule an event
class RescheduleEventArgs(BaseModel):
    event_name: str = Field(description="name of the event to be rescheduled")
    new_start_date_time: datetime = Field(description="new start date and time of the event")
    length_hours: int = Field(description="new length of the event")

def reschedule_event(event_name: str, new_start_date_time: datetime, length_hours: int):
    # Retrieve events in the upcoming week
    from_datetime = new_start_date_time.replace(hour=0, minute=0, second=0, microsecond=0)
    to_datetime = new_start_date_time.replace(hour=23, minute=59, second=59, microsecond=999999)

    events = calendar.get_events(calendar_id="nikki617@bu.edu", time_min=from_datetime, time_max=to_datetime)

    # Debug: Print out the retrieved events for verification
    print("Retrieved Events for Rescheduling:")
    for event in events:
        print(f"- {event.summary} at {event.start} to {event.end}")

    # Look for the event with the matching name
    for event in events:
        if event.summary == event_name:
            # If found, cancel the event first
            cancel_event(event_name, from_datetime, to_datetime)

            # Then add the new event
            add_event(new_start_date_time, length_hours, event_name)
            return f"Event '{event_name}' has been rescheduled to {new_start_date_time}."

    return f"No event named '{event_name}' was found to reschedule."
