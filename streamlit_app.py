import streamlit as st
import openai
import pandas as pd
import numpy as np
import google.auth
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Load the secrets
openai_api_key = st.secrets["openai"]["api_key"]

# Set up OpenAI
openai.api_key = openai_api_key

# Load Google Calendar API credentials
google_credentials = st.secrets["CalendarAPI"]

# Initialize Google Calendar API client
credentials = service_account.Credentials.from_service_account_info(
    google_credentials,
    scopes=["https://www.googleapis.com/auth/calendar"]
)
service = build('calendar', 'v3', credentials=credentials)

# Streamlit UI
st.title("Smart Meeting Scheduler with AI Integration")
st.sidebar.header("Settings")

def get_events(calendar_id='primary'):
    """Fetch events from Google Calendar."""
    events_result = service.events().list(calendarId=calendar_id, singleEvents=True, orderBy='startTime').execute()
    return events_result.get('items', [])

def add_event(event):
    """Add a new event to Google Calendar."""
    service.events().insert(calendarId='primary', body=event).execute()
    st.success("Event added successfully!")

def generate_meeting_notes(prompt):
    """Generate meeting notes using OpenAI API."""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response['choices'][0]['message']['content']

st.sidebar.subheader("Fetch Events")
if st.sidebar.button("Get Upcoming Events"):
    events = get_events()
    if not events:
        st.write("No upcoming events found.")
    else:
        st.write("Upcoming Events:")
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            st.write(f"{start}: {event['summary']}")

st.sidebar.subheader("Add Event")
event_title = st.sidebar.text_input("Event Title")
event_start = st.sidebar.date_input("Start Date")
event_time_start = st.sidebar.time_input("Start Time")
event_end = st.sidebar.date_input("End Date")
event_time_end = st.sidebar.time_input("End Time")
event_description = st.sidebar.text_area("Description")

if st.sidebar.button("Add Event"):
    event_start_datetime = f"{event_start}T{event_time_start}:00"
    event_end_datetime = f"{event_end}T{event_time_end}:00"

    event = {
        'summary': event_title,
        'description': event_description,
        'start': {
            'dateTime': event_start_datetime,
            'timeZone': 'America/New_York',  # Change this to your timezone
        },
        'end': {
            'dateTime': event_end_datetime,
            'timeZone': 'America/New_York',  # Change this to your timezone
        },
    }
    
    add_event(event)

st.sidebar.subheader("Generate Meeting Notes")
meeting_prompt = st.sidebar.text_area("Meeting Prompt")

if st.sidebar.button("Generate Notes"):
    if meeting_prompt:
        notes = generate_meeting_notes(meeting_prompt)
        st.write("Generated Meeting Notes:")
        st.write(notes)
    else:
        st.warning("Please enter a prompt for the meeting notes.")
