# calendar_integration.py

# gcsa imports
from gcsa.event import Event
from gcsa.google_calendar import GoogleCalendar
from google.oauth2 import service_account
from pydantic import BaseModel, Field
from datetime import datetime
import json

# Connecting to the Google Calendar through an API

# Get the credentials from Secrets.
def get_calendar():
    credentials = service_account.Credentials.from_service_account_info(
        json.loads(st.secrets["MYJSON"]),
        scopes=["https://www.googleapis.com/auth/calendar"]
    )
    return GoogleCalendar(credentials=credentials)

# Parameters needed to look for an event
class GetEventArgs(BaseModel):
    from_datetime: datetime = Field(description="beginning of date range to retrieve events")
    to_datetime: datetime = Field(description="end of date range to retrieve events")

# Define the tool for getting events
def get_events(from_datetime, to_datetime):
    calendar = get_calendar()
    events = calendar.get_events(calendar_id="mndhamod@gmail.com", time_min=from_datetime, time_max=to_datetime)
    return list(events)

# Create a Tool object for getting events 
list_event_tool = StructuredTool(
    name="GetEvents",
    func=get_events,
    args_schema=GetEventArgs,
    description="Useful for getting the list of events from the user's calendar."
)

# Parameters needed to add an event
class AddEventArgs(BaseModel):
    start_date_time: datetime = Field(description="start date and time of event")
    length_hours: int = Field(description="length of event")
    event_name: str = Field(description="name of the event")

# Define the tool for adding events
def add_event(start_date_time, length_hours, event_name):
    calendar = get_calendar()
    start = start_date_time
    end = start + length_hours * 3600  # Convert hours to seconds
    event = Event(event_name, start=start, end=end)
    return calendar.add_event(event, calendar_id="mndhamod@gmail.com")

# Create a Tool object for adding events 
add_event_tool = StructuredTool(
    name="AddEvent",
    func=add_event,
    args_schema=AddEventArgs,
    description="Useful for adding an event with a start date, event name, and length in hours."
)

# Update this list with the new tools
tools = [list_event_tool, add_event_tool]
