import streamlit as st
import json
from google.oauth2 import service_account
from gcsa.google_calendar import GoogleCalendar
import datetime

# Load the credentials from Streamlit secrets
credentials = service_account.Credentials.from_service_account_info(
    json.loads(st.secrets["CalendarAPI"]),
    scopes=["https://www.googleapis.com/auth/calendar"]
)

# Create the GoogleCalendar object with the credentials
calendar = GoogleCalendar(credentials=credentials)

# Display the title in the Streamlit app
st.title("Google Calendar Event Viewer")

# Input for Calendar ID
calendar_id = st.text_input("Enter your Calendar ID:", value="nikki617@bu.edu")

# Input for date range
start_date = st.date_input("Start Date", value=datetime.date.today())
end_date = st.date_input("End Date", value=datetime.date.today() + datetime.timedelta(days=30))

st.write("Events from your Google Calendar:")

try:
    with st.spinner("Loading events..."):
        # Fetch all events
        events = list(calendar.get_events(calendar_id=calendar_id, start=start_date, end=end_date))

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
    st.error(f"An error occurred: {str(e)}")
