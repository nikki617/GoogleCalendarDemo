# calendar_integration.py

# gcsa imports
from gcsa.event import Event
from gcsa.google_calendar import GoogleCalendar
from google.oauth2 import service_account
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
import streamlit as st

# Connecting to the Google Calendar through an API
def connect_calendar():
    # Get the credentials from Secrets.
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["CalendarAPI"],
        scopes=["https://www.googleapis.com/auth/calendar"]
    )
    return GoogleCalendar(credentials=credentials)

# Parameters needed to look for an event
class GetEventArgs(BaseModel):
    from_datetime: datetime = Field(description="beginning of date range to retrieve events")
    to_datetime: datetime = Field(description="end of date range to retrieve events")

# Define the tool for getting events 
def get_events(calendar, from_datetime, to_datetime):
    current_year = datetime.now().year
    from_datetime = from_datetime.replace(year=current_year)
    to_datetime = to_datetime.replace(year=current_year)
    
    events = calendar.get_events(calendar_id="nikki617@bu.edu", time_min=from_datetime, time_max=to_datetime)
    return list(events)

# Parameters needed to add an event
class AddEventArgs(BaseModel):
    start_date_time: datetime = Field(description="start date and time of event")
    length_hours: int = Field(description="length of event")
    event_name: str = Field(description="name of the event")

# Define the tool for adding events 
# calendar_integration.py

def add_event(calendar, start_date_time, length_hours, event_name):
    # Convert start_date_time to a datetime object
    start = datetime.fromisoformat(start_date_time.replace("Z", "+00:00"))  # Ensure proper UTC handling
    end = start + timedelta(hours=length_hours)  # Use timedelta for adding hours

    # Create event data for Google Calendar
    event = {
        'summary': event_name,
        'start': {
            'dateTime': start.isoformat(),
            'timeZone': 'UTC',  # Set your desired timezone
        },
        'end': {
            'dateTime': end.isoformat(),
            'timeZone': 'UTC',
        },
    }

    # Insert event into Google Calendar
    event_result = calendar.events().insert(calendarId='nikki617@bu.edu', body=event).execute()
    return event_result
