import openai
import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta

# Access API keys from Streamlit secrets
openai.api_key = st.secrets["openai"]["api_key"]

# Get Google Calendar credentials from secrets
calendar_credentials = {
    "type": st.secrets["CalendarAPI"]["type"],
    "project_id": st.secrets["CalendarAPI"]["project_id"],
    "private_key_id": st.secrets["CalendarAPI"]["private_key_id"],
    "private_key": st.secrets["CalendarAPI"]["private_key"],
    "client_email": st.secrets["CalendarAPI"]["client_email"],
    "client_id": st.secrets["CalendarAPI"]["client_id"],
    "auth_uri": st.secrets["CalendarAPI"]["auth_uri"],
    "token_uri": st.secrets["CalendarAPI"]["token_uri"],
    "auth_provider_x509_cert_url": st.secrets["CalendarAPI"]["auth_provider_x509_cert_url"],
    "client_x509_cert_url": st.secrets["CalendarAPI"]["client_x509_cert_url"],
}

# Authenticate with Google Calendar using the service account credentials
credentials = service_account.Credentials.from_service_account_info(calendar_credentials)
service = build('calendar', 'v3', credentials=credentials)

# Function to fetch Google Calendar events
def fetch_google_calendar_events():
    now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                          maxResults=10, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        st.write('No upcoming events found.')
    else:
        st.write('Upcoming events:')
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            st.write(f"{start}: {event['summary']}")

# Function to create Google Calendar events
def create_google_calendar_event(event_summary, event_start, event_end):
    event = {
        'summary': event_summary,
        'start': {
            'dateTime': event_start,
            'timeZone': 'UTC',
        },
        'end': {
            'dateTime': event_end,
            'timeZone': 'UTC',
        },
    }
    created_event = service.events().insert(calendarId='primary', body=event).execute()
    st.write(f"Event created: {created_event.get('htmlLink')}")

# Main Streamlit app logic
st.title("Smart Meeting Scheduler")

# Get OpenAI completion (example usage)
st.write("Let's use OpenAI API!")
response = openai.Completion.create(
    engine="text-davinci-003",
    prompt="What is the current weather?",
    max_tokens=50
)
st.write(response.choices[0].text)

# Button to fetch Google Calendar events
if st.button("Show Upcoming Events"):
    fetch_google_calendar_events()

# Example event creation (you can replace with user inputs)
if st.button("Create Event"):
    event_summary = "Test Event"
    event_start = (datetime.utcnow() + timedelta(hours=1)).isoformat() + 'Z'
    event_end = (datetime.utcnow() + timedelta(hours=2)).isoformat() + 'Z'
    create_google_calendar_event(event_summary, event_start, event_end)
