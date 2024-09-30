from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class Calendar:
    def __init__(self, credentials_info, calendar_id, timezone='America/New_York'):
        self.timezone = timezone
        self.calendar_id = calendar_id
        self.service = self._create_service(credentials_info)

    def _create_service(self, credentials_info):
        scopes = ['https://www.googleapis.com/auth/calendar']
        credentials = service_account.Credentials.from_service_account_info(
            credentials_info, scopes=scopes
        )
        service = build('calendar', 'v3', credentials=credentials)
        return service

    def get_calendar_events(self, start_range, end_range):
        from_dt = start_range.isoformat() + 'Z'
        to_dt = end_range.isoformat() + 'Z'

        try:
            events_result = self.service.events().list(
                calendarId=self.calendar_id,
                timeMin=from_dt,
                timeMax=to_dt,
                timeZone=self.timezone
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

    def add_event(self, event_summary, start_datetime, end_datetime, event_location=None):
        event = {
            'summary': event_summary,
            'start': {
                'dateTime': start_datetime.isoformat(),
                'timeZone': self.timezone,
            },
            'end': {
                'dateTime': end_datetime.isoformat(),
                'timeZone': self.timezone,
            },
            'location': event_location,
        }

        try:
            self.service.events().insert(calendarId=self.calendar_id, body=event).execute()
            return "Event added successfully."
        except HttpError as e:
            return (f"Failed to add event to the calendar: {e}")

    def update_event(self, event_id, new_summary=None, new_start=None, new_end=None, new_location=None):
        try:
            event = self.service.events().get(calendarId=self.calendar_id, eventId=event_id).execute()
            if new_summary:
                event['summary'] = new_summary
            if new_start:
                event['start']['dateTime'] = new_start.isoformat()
            if new_end:
                event['end']['dateTime'] = new_end.isoformat()
            if new_location:
                event['location'] = new_location

            updated_event = self.service.events().update(calendarId=self.calendar_id, eventId=event_id, body=event).execute()
            return f"Event updated: {updated_event.get('htmlLink')}"
        except HttpError as e:
            return (f"Failed to update event: {e}")

    def delete_event(self, event_id):
        try:
            self.service.events().delete(calendarId=self.calendar_id, eventId=event_id).execute()
            return "Event deleted successfully."
        except HttpError as e:
            return (f"Failed to delete event: {e}")
