from gcsa.event import Event
from gcsa.google_calendar import GoogleCalendar
from google.oauth2 import service_account
from datetime import datetime, timedelta
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
    event_name: str = Field(description="name of the event")
    event_date_time: datetime = Field(description="date and time of the event")

# Define the function to cancel an event
def cancel_event(event_name: str, event_date_time: datetime):
    current_year = datetime.now().year
    event_date_time = event_date_time.replace(year=current_year)
    
    events = calendar.get_events(time_min=event_date_time - timedelta(days=1), time_max=event_date_time + timedelta(days=1))
    
    for event in events:
        if event.summary == event_name and event.start == event_date_time:
            calendar.delete_event(event)
            return f"Event '{event_name}' on {event_date_time.strftime('%B %d, %Y at %I:%M %p')} has been canceled."
    
    return f"I couldn't find an event named '{event_name}' on {event_date_time.strftime('%B %d, %Y at %I:%M %p')} to cancel."
