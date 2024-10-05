import streamlit as st
import openai
import pandas as pd
from datetime import datetime, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Load secrets
secrets = st.secrets

# OpenAI API Key
openai.api_key = secrets["openai"]["api_key"]

# Google Calendar API credentials
credentials = service_account.Credentials.from_service_account_info(
    {
        "type": secrets["CalendarAPI"]["type"],
        "project_id": secrets["CalendarAPI"]["project_id"],
        "private_key_id": secrets["CalendarAPI"]["private_key_id"],
        "private_key": secrets["CalendarAPI"]["private_key"].replace('\\n', '\n'),  # Ensure newlines are correct
        "client_email": secrets["CalendarAPI"]["client_email"],
        "client_id": secrets["CalendarAPI"]["client_id"],
        "auth_uri": secrets["CalendarAPI"]["auth_uri"],
        "token_uri": secrets["CalendarAPI"]["token_uri"],
        "auth_provider_x509_cert_url": secrets["CalendarAPI"]["auth_provider_x509_cert_url"],
        "client_x509_cert_url": secrets["CalendarAPI"]["client_x509_cert_url"],
    }
)

# Build the Google Calendar API service
service = build('calendar', 'v3', credentials=credentials)

# Function to list upcoming events
def list_events():
    now = datetime.utcnow().isoformat() + 'Z'  # Current time
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                          maxResults=10, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])
    
    if not events:
        return "No upcoming events found."
    
    event_data = []
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        event_data.append({"summary": event['summary'], "start": start})

    return pd.DataFrame(event_data)

# Function to create an event
def create_event(summary, start_time, end_time):
    event = {
        'summary': summary,
        'start': {
            'dateTime': start_time,
            'timeZone': 'UTC',
        },
        'end': {
            'dateTime': end_time,
            'timeZone': 'UTC',
        },
    }
    event = service.events().insert(calendarId='primary', body=event).execute()
    return f"Event created: {event.get('htmlLink')}"

# Streamlit UI
st.title("Smart Meeting Scheduler with AI Integration")

# List Events
if st.button("List Upcoming Events"):
    events_df = list_events()
    st.write(events_df)

# Create Event
st.subheader("Create a New Event")
summary = st.text_input("Event Summary")

# Set default datetime values for inputs
current_time = datetime.now()
start_time = st.date_input("Start Date", current_time.date())
start_hour = st.time_input("Start Time", current_time.time())
end_time = st.time_input("End Time", (current_time + timedelta(hours=1)).time())

# Combine date and time into a single datetime object
start_datetime = datetime.combine(start_time, start_hour)
end_datetime = datetime.combine(start_time, end_time)

if st.button("Create Event"):
    if summary and start_datetime and end_datetime:
        if start_datetime < end_datetime:
            result = create_event(summary, start_datetime.isoformat(), end_datetime.isoformat())
            st.success(result)
        else:
            st.error("End time must be after start time.")
    else:
        st.error("Please fill in all fields.")

# ChatGPT Integration
st.subheader("Ask a Question to AI")
user_query = st.text_input("Your question here...")

if st.button("Get AI Response"):
    if user_query:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": user_query}
            ]
        )
        ai_response = response['choices'][0]['message']['content']
        st.write(ai_response)
    else:
        st.error("Please enter a question.")
