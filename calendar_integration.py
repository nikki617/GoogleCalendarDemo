import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build

class CalendarIntegration:
    def __init__(self):
        self.credentials = self.get_credentials()
        self.service = self.create_service()

    def get_credentials(self):
        try:
            service_account_info = st.secrets['CalendarAPI']
            creds = service_account.Credentials.from_service_account_info(service_account_info)
            return creds
        except Exception as e:
            st.error(f"Error loading credentials: {e}")
            return None

    def create_service(self):
        try:
            return build('calendar', 'v3', credentials=self.credentials)
        except Exception as e:
            st.error(f"Error creating Google Calendar service: {e}")
            return None

    def list_events(self):
        if self.service:
            events_result = self.service.events().list(calendarId='primary', maxResults=10).execute()
            return events_result.get('items', [])
        return []
