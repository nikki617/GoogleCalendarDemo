from gcsa.google_calendar import GoogleCalendar
from gcsa.event import Event
from datetime import datetime

def authenticate_google_calendar(credentials):
    # Initialize Google Calendar with credentials
    return GoogleCalendar(credentials=credentials)

def check_availability(service, start_date, end_date):
    try:
        # Fetch events from the calendar within the provided range
        events = service.get_events(time_min=start_date, time_max=end_date)
        event_list = []
        for event in events:
            # Convert event start and end to datetime if they are strings
            start = event.start if isinstance(event.start, datetime) else datetime.fromisoformat(event.start)
            end = event.end if isinstance(event.end, datetime) else datetime.fromisoformat(event.end)
            
            event_list.append({
                "summary": event.summary,
                "start": start.isoformat(),
                "end": end.isoformat()
            })
        return event_list
    except Exception as e:
        raise Exception(f"Error fetching events: {e}")

def book_event(service, start_time, end_time, summary):
    event = Event(
        summary=summary,
        start=start_time,
        end=end_time,
        timezone='America/New_York'
    )
    return service.add_event(event)
