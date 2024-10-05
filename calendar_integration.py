from gcsa.google_calendar import GoogleCalendar
from datetime import datetime

def authenticate_google_calendar(credentials):
    return GoogleCalendar(credentials=credentials)

def check_availability(service, start_date, end_date):
    events = []
    for event in service.get_events(time_min=start_date, time_max=end_date):
        events.append(event)
    return events

def book_event(service, start_time, end_time, summary):
    event = {
        'summary': summary,
        'start': {'dateTime': start_time, 'timeZone': 'America/New_York'},
        'end': {'dateTime': end_time, 'timeZone': 'America/New_York'},
    }
    return service.add_event(event)
