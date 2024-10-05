import streamlit as st
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Load Google Calendar API credentials from Streamlit secrets
if "CalendarAPI" in st.secrets:
    calendar_api = st.secrets["CalendarAPI"]

    # Extract the credentials
    type_ = calendar_api["type"]
    project_id = calendar_api["project_id"]
    private_key_id = calendar_api["private_key_id"]
    private_key = calendar_api["private_key"]
    client_email = calendar_api["client_email"]
    client_id = calendar_api["client_id"]
    auth_uri = calendar_api["auth_uri"]
    token_uri = calendar_api["token_uri"]
    auth_provider_x509_cert_url = calendar_api["auth_provider_x509_cert_url"]
    client_x509_cert_url = calendar_api["client_x509_cert_url"]

    # Create credentials object
    credentials = service_account.Credentials.from_service_account_info(calendar_api)

    # Build the Google Calendar API service
    service = build('calendar', 'v3', credentials=credentials)

    st.title("Google Calendar Integration")

    # Example functionality: list upcoming events
    st.subheader("Upcoming Events")

    # Call the Calendar API
    now = '2024-10-01T00:00:00Z'  # Replace with your desired time
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                          maxResults=10, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        st.write('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        st.write(f"{start}: {event['summary']}")

else:
    st.error("CalendarAPI secrets not found!")
