# gcsa imports
from gcsa.event import Event
from gcsa.google_calendar import GoogleCalendar
from google.oauth2 import service_account
import streamlit as st

# Constants
CALENDAR_ID = "nikki617@bu.edu"
SCOPES = ["https://www.googleapis.com/auth/calendar"]

def initialize_calendar():
    """Initialize Google Calendar API."""
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["CalendarAPI"],
        scopes=SCOPES
    )
    return GoogleCalendar(credentials=credentials)

def main():
    """Main function to run the Streamlit app."""
    calendar = initialize_calendar()
    # Further implementation...

if __name__ == "__main__":
    main()
