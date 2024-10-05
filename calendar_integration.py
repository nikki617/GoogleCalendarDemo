from gcsa.google_calendar import GoogleCalendar
from gcsa.event import Event
from datetime import datetime, time

def authenticate_google_calendar(credentials):
    # Initialize Google Calendar with credentials
    return GoogleCalendar(credentials=credentials)

def check_availability(service, start_date, end_date):
    try:
        # Fetch events from the calendar within the provided range
        events = service.get_events(time_min=start_date, time_max=end_date)
        event_list = []
        for event in events:
            # Ensure that event start and end are datetime objects
            start = event.start
            end = event.end

            # If event start or end are strings, convert them to datetime
            if isinstance(start, str):
                start = datetime.fromisoformat(start)
            if isinstance(end, str):
                end = datetime.fromisoformat(end)

            # Handle the case where date and time might need combining
            if isinstance(start, str):
                start = datetime.strptime(start, '%Y-%m-%d').date()  # convert to date
                start = datetime.combine(start, time(0, 0))  # combine with time if needed
            
            if isinstance(end, str):
                end = datetime.strptime(end, '%Y-%m-%d').date()  # convert to date
                end = datetime.combine(end, time(23, 59))  # combine with time if needed
            
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
