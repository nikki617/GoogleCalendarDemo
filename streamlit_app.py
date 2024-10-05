import streamlit as st
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Title of the Streamlit app
st.title("Google Calendar API Integration")

# Load credentials from Streamlit secrets (individual fields)
credentials = service_account.Credentials.from_service_account_info(
    {
        "type": st.secrets["CalendarAPI"]["type"],
        "project_id": st.secrets["CalendarAPI"]["project_id"],
        "private_key_id": st.secrets["CalendarAPI"]["private_key_id"],
        "private_key": st.secrets["CalendarAPI"]["private_key"],
        "client_email": st.secrets["CalendarAPI"]["client_email"],
        "client_id": st.secrets["CalendarAPI"]["client_id"],
        "auth_uri": st.secrets["CalendarAPI"]["auth_uri"],
        "token_uri": st.secrets["CalendarAPI"]["token_uri"],
        "auth_provider_x509_cert_url": st.secrets["CalendarAPI"]["auth_provider_x509_cert_url"],
        "client_x509_cert_url": st.secrets["CalendarAPI"]["client_x509_cert_url"]
    },
    scopes=["https://www.googleapis.com/auth/calendar"]
)

# Build the Google Calendar service
service = build("calendar", "v3", credentials=credentials)

# Get the user's primary calendar events
def get_calendar_events():
    try:
        # Get the list of events from the primary calendar
        events_result = service.events().list(calendarId="primary", maxResults=10).execute()
        events = events_result.get('items', [])
        if not events:
            st.write("No upcoming events found.")
        else:
            st.write("Upcoming events:")
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                st.write(f"{start}: {event['summary']}")
    except Exception as e:
        st.error(f"An error occurred: {e}")

# Button to display calendar events
if st.button("Get Calendar Events"):
    get_calendar_events()
