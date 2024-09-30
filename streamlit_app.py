import streamlit as st
import json
from google.oauth2 import service_account
from gcsa.google_calendar import GoogleCalendar

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
    # Fetch all events
    events = list(calendar.get_events(calendar_id=calendar_id))  # Specify calendar ID

    # Iterate through and display events
    if events:
        for event in events:
            st.write(f"**Event:** {event.summary}")
            st.write(f"**Start:** {event.start.isoformat()}")
            st.write(f"**End:** {event.end.isoformat()}")
            st.write("---")
    else:
        st.write("No events found.")
except Exception as e:
    st.error(f"An error occurred: {e}")
