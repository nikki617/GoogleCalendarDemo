from gcsa.google_calendar import GoogleCalendar

def authenticate_google_calendar(credentials):
    return GoogleCalendar(credentials=credentials)

def check_availability(service, start_date, end_date):
    return service.get_events(start=start_date, end=end_date)

def book_event(service, start_time, end_time, summary):
    event = {
        'summary': summary,
        'start': {'dateTime': start_time, 'timeZone': 'America/New_York'},
        'end': {'dateTime': end_time, 'timeZone': 'America/New_York'},
    }
    return service.add_event(event)
