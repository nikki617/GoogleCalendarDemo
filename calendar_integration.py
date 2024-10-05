import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta

class CalendarIntegration:
    def __init__(self):
        self.credentials = self.get_credentials()
        self.service = build('calendar', 'v3', credentials=self.credentials)
        self.calendar_id = os.getenv('CALENDAR_ID')  # Use this if you have set it in your environment variables
        # If using Streamlit secrets, you might want to set it like this instead:
        self.calendar_id = os.environ.get("CALENDAR_ID")  # Replace with the method you're using

    def get_credentials(self):
        # Load credentials from Streamlit secrets
        creds = Credentials.from_service_account_info(st.secrets['CalendarAPI'])
        return creds

    def get_calendar_events(self, start_range, end_range):
        from_dt = start_range.isoformat() + 'Z'
        to_dt = end_range.isoformat() + 'Z'

        try:
            events_result = self.service.events().list(
                calendarId=self.calendar_id,
                timeMin=from_dt,
                timeMax=to_dt,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            events = events_result.get('items', [])
            calendar_events = []
            for event in events:
                summary = event.get('summary', 'No summary')
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))

                calendar_events.append({
                    'summary': summary,
                    'start': start,
                    'end': end
                })

            return calendar_events

        except HttpError as e:
            print(f"An error occurred: {e}")
            return []
