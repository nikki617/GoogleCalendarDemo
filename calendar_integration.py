from google.oauth2 import service_account
from gcsa.google_calendar import GoogleCalendar

def authenticate_google_calendar(credentials):
    return GoogleCalendar(credentials=credentials)

def check_availability(service, start_date, end_date):
    """
    This function fetches events between the start_date and end_date from Google Calendar.
    """
    return service.get_events(time_min=start_date, time_max=end_date)

def book_event(service, start_time, end_time, summary):
    event = {
        'summary': summary,
        'start': {'dateTime': start_time, 'timeZone': 'America/New_York'},
        'end': {'dateTime': end_time, 'timeZone': 'America/New_York'},
    }
    return service.insert_event(event)

def update_event(service, event_id, start_time, end_time):
    event = service.get_event(event_id)
    event['start']['dateTime'] = start_time
    event['end']['dateTime'] = end_time
    return service.update_event(event)

def delete_event(service, event_id):
    service.delete_event(event_id)
