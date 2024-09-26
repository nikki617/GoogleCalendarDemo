import streamlit as st
import json
from google.oauth2 import service_account
from gcsa.google_calendar import GoogleCalendar

# Load and parse the credentials from Streamlit secrets
credentials_info = json.loads(st.secrets["CalendarAPI"])

# Use the credentials for service account authentication
credentials = service_account.Credentials.from_service_account_info(credentials_info)

# Initialize GoogleCalendar with the credentials
calendar = GoogleCalendar(credentials=credentials)

# Retrieve and display existing events from the Google Calendar
st.write("Retrieving events from your Google Calendar...")

# Iterate over events and display each one in the Streamlit app
for event in calendar:
    st.write(event)
