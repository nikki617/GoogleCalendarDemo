# gcsa imports
from gcsa.event import Event
from gcsa.google_calendar import GoogleCalendar
from gcsa.recurrence import Recurrence, DAILY, SU, SA
from google.oauth2 import service_account

import streamlit as st

##-------------------
## Connecting to the Google Calendar through an API

# Get the credentials from Secrets.
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["CalendarAPI"],  # st.secrets is already a dict, so use directly
    scopes=["https://www.googleapis.com/auth/calendar"]
)
