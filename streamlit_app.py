import streamlit as st
from gcsa.google_calendar import GoogleCalendar

# Retrieve Google Calendar secret from Streamlit's secrets
GoogleCalendarSecret = st.secrets["CalendarAPI"]

# Initialize Google Calendar using your email
calendar = GoogleCalendar('nikki617@bu.edu')

# Loop through the events in the calendar and display them
st.write("Retrieving events from your Google Calendar...")

# Iterate over events and display each one in the Streamlit app
for event in calendar:
    st.write(event)
