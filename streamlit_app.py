import streamlit as st
import json
from google.oauth2 import service_account
from gcsa.google_calendar import GoogleCalendar, Event
from datetime import datetime, timedelta

# Load and parse the credentials from Streamlit secrets
credentials_info = json.loads(st.secrets["CalendarAPI"])

# Use the credentials for service account authentication
credentials = service_account.Credentials.from_service_account_info(credentials_info)

# Initialize GoogleCalendar with the credentials
calendar = GoogleCalendar(credentials=credentials)

# Display a title for the Streamlit app
st.title("Google Calendar Event Manager")

# Function to retrieve and display events
def display_events():
    st.write("Retrieving events from your Google Calendar...")

    # Retrieve events from the Google Calendar
    events = list(calendar.get_events(time_min=datetime.now(), time_max=datetime.now() + timedelta(days=7)))

    # Display each event
    if events:
        for event in events:
            st.write(f"Event: {event.summary}, Start: {event.start}, End: {event.end}")
    else:
        st.write("No events found for the next 7 days.")

# Function to add a new event
def add_event():
    st.write("Add a new event to your calendar")

    event_summary = st.text_input("Event summary", "Meeting")
    event_start = st.date_input("Event start date", datetime.now())
    event_end = st.date_input("Event end date", datetime.now() + timedelta(hours=1))

    if st.button("Add Event"):
        new_event = Event(
            event_summary,
            start=event_start,
            end=event_end,
            timezone='America/New_York'
        )
        calendar.add_event(new_event)
        st.success(f"Event '{event_summary}' added successfully!")

# Streamlit interface options
st.sidebar.title("Menu")
option = st.sidebar.selectbox("Choose an option", ("View Events", "Add Event"))

if option == "View Events":
    display_events()
elif option == "Add Event":
    add_event()
