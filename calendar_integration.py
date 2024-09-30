# calendar_integration.py

from google.oauth2 import service_account
from gcsa.google_calendar import GoogleCalendar

# Load the service account credentials from Streamlit secrets
def authenticate_google_calendar():
    import streamlit as st
    credentials_info = st.secrets["CalendarAPI"]
    
    # Convert the AttrDict to a standard dictionary if necessary
    credentials = service_account.Credentials.from_service_account_info(dict(credentials_info))
    
    # Initialize the Google Calendar API
    return GoogleCalendar(credentials=credentials)

def check_av(calendar, start_time, end_time):
    events = calendar.get_events(start=start_time, end=end_time)
    return events
