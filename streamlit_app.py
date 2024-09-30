import streamlit as st
import json
from google.oauth2 import service_account
from gcsa.event import Event
from gcsa.google_calendar import GoogleCalendar
from datetime import datetime, timedelta  # Import timedelta

# Deviations from documentation:
# 1- Creating a service account and creating a key for it.
# 2- Adding the service account email to your calendar as a user with event edit permissions.
# 3- Using service_account.Credentials.from_service_account_info instead of credentials_path for security reasons.
# 4- Putting the JSON in Streamlit secrets and using json.loads rather than uploading the file to GitHub for security.

# Load the credentials from Streamlit secrets
credentials = service_account.Credentials.from_service_account_info(
    json.loads(st.secrets["CalendarAPI"]),
    scopes=["https://www.googleapis.com/auth/calendar"]
)

# Create the GoogleCalendar object with the credentials
calendar = GoogleCalendar(credentials=credentials)

# Display the title in the Streamlit app
st.title("Google Calendar Event Viewer")

# Get and display the list of events from the specified calendar
calendar_id = "mndhamod@gmail.com"  # Replace with your calendar ID

st.write("Events from your Google Calendar:")

try:
    # Fetch events for the next 7 days
    events = list(calendar.get_events(time_min=datetime.now(), time_max=datetime.now() + timedelta(days=7)))

    # Iterate through and display events
    if events:
        for event in events:
            st.write(f"Event: {event.summary}, Start: {event.start}, End: {event.end}")
    else:
        st.write("No events found for the next 7 days.")
except Exception as e:
    st.error(f"An error occurred: {e}")
