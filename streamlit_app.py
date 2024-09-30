import streamlit as st
import json
from google.oauth2 import service_account
from gcsa.event import Event
from gcsa.google_calendar import GoogleCalendar
from datetime import datetime, timedelta

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
calendar_id = "nikki617@bu.edu"  # Replace with your calendar ID

st.write("Events from your Google Calendar:")

try:
    # Fetch events for the next 7 days
    events = list(calendar.get_events(time_min=datetime.now(), time_max=datetime.now() + timedelta(days=7)))

    # Iterate through and display events
    if events:
        for event in events:
            st.write(f"**Event:** {event.summary}")
            st.write(f"**Start:** {event.start.isoformat()}")
            st.write(f"**End:** {event.end.isoformat()}")
            st.write("---")
    else:
        st.write("No events found for the next 7 days.")
except Exception as e:
    st.error(f"An error occurred: {e}")
