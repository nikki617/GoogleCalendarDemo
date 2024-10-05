# calendar_integration.py

# gcsa imports
from gcsa.event import Event
from gcsa.google_calendar import GoogleCalendar
from google.oauth2 import service_account
from pydantic import BaseModel, Field
from datetime import datetime
import streamlit as st

## Connecting to the Google Calendar through an API

# Get the credentials from Secrets.
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["CalendarAPI"],  # st.secrets is already a dict, so use directly
    scopes=["https://www.googleapis.com/auth/calendar"]
)

# Create the GoogleCalendar.
calendar = GoogleCalendar(credentials=credentials)

# Event listing tool

# Parameters needed to look for an event
class GetEventArgs(BaseModel):
    from_datetime: datetime = Field(description="beginning of date range to retrieve events")
    to_datetime: datetime = Field(description="end of date range to retrieve events")

# Define the tool 
def get_events(from_datetime: datetime, to_datetime: datetime):
    # Ensure that the current year is used by default
    current_year = datetime.now().year
    from_datetime = from_datetime.replace(year=current_year)
    to_datetime = to_datetime.replace(year=current_year)
    
    events = calendar.get_events(calendar_id="nikki617@bu.edu", time_min=from_datetime, time_max=to_datetime)
    return list(events)

# Event adding tool

# Parameters needed to add an event
class AddEventArgs(BaseModel):
    start_date_time: datetime = Field(description="start date and time of event")
    length_hours: int = Field(description="length of event")
    event_name: str = Field(description="name of the event")

# Define the tool 
def add_event(start_date_time: datetime, length_hours: int, event_name: str):
    # Ensure the current year is used
    current_year = datetime.now().year
    start_date_time = start_date_time.replace(year=current_year)
    start = start_date_time
    end = start + timedelta(hours=length_hours)
    event = Event(event_name, start=start, end=end)
    return calendar.add_event(event, calendar_id="nikki617@bu.edu")

