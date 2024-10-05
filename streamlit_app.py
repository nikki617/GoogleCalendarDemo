import openai
import streamlit as st
from gcsa.google_calendar import GoogleCalendar
from gcsa.event import Event
from dateutil.parser import parse
import datetime
import pytz

# Access API keys from secrets
openai.api_key = st.secrets["openai"]["api_key"]
CREDENTIALS_PATH = st.secrets["CalendarAPI"]  # Google Calendar credentials

EMAIL = st.secrets["CalendarAPI"]["client_email"]  # Email for Google Calendar

# Define your functions and app logic
def create_google_calendar_events(events_string: str):
    gc = GoogleCalendar(EMAIL, credentials=CREDENTIALS_PATH)
    created_events = []

    events = events_string.split(';')
    for event_str in events:
        event_parts = event_str.split(',')
        
        if len(event_parts) < 3:
            raise ValueError("Each event string must have at least summary, start, and end details.")
        
        summary = event_parts[0]
        start_str = event_parts[1]
        end_str = event_parts[2]
        
        start = parse(start_str)
        end = parse(end_str)

        event = Event(summary, start=start, end=end)
        created_event = gc.add_event(event)
        created_events.append(created_event)
        
    return created_events

def fetch_google_calendar_events(start_time, end_time, query=None, single_events=False):
    start_time = parse(start_time)
    end_time = parse(end_time)
    
    gc = GoogleCalendar(EMAIL, credentials=CREDENTIALS_PATH)
    events = list(gc.get_events(time_min=start_time, time_max=end_time, query=query, single_events=single_events))
    
    return [{
        "event_id": event.event_id,
        "summary": event.summary,
        "start": str(event.start),
        "end": str(event.end),
        "description": event.description
    } for event in events]

# Main logic for scheduling (same as before)
