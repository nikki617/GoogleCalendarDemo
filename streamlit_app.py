import streamlit as st
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

# Function to authenticate and create a Google Calendar service
def authenticate_google_calendar():
    creds = None
    # Load credentials from file or environment variable
    # Make sure to replace this with your actual method to get credentials
    creds = Credentials.from_authorized_user_file('credentials.json', ['https://www.googleapis.com/auth/calendar'])
    return build('calendar', 'v3', credentials=creds)

# Function to add an event to Google Calendar
def add_event(calendar, start_date_time, length_hours, event_name):
    if isinstance(start_date_time, str):
        start_date_time = datetime.fromisoformat(start_date_time.replace("Z", "+00:00"))

    start = start_date_time.isoformat() + 'Z'  # 'Z' indicates UTC time
    end = (start_date_time + timedelta(hours=length_hours)).isoformat() + 'Z'

    event = {
        'summary': event_name,
        'start': {
            'dateTime': start,
            'timeZone': 'UTC',
        },
        'end': {
            'dateTime': end,
            'timeZone': 'UTC',
        },
    }

    try:
        calendar.events().insert(calendarId='primary', body=event).execute()
        st.success(f"Event '{event_name}' added successfully.")
    except Exception as e:
        st.error(f"An error occurred: {e}")

# Function to get events from Google Calendar
def get_events(calendar, from_datetime, to_datetime):
    events_result = calendar.events().list(calendarId='primary', timeMin=from_datetime,
                                           timeMax=to_datetime,
                                           singleEvents=True,
                                           orderBy='startTime').execute()
    return events_result.get('items', [])

# Function to delete an event from Google Calendar
def delete_event(calendar, event_id):
    try:
        calendar.events().delete(calendarId='primary', eventId=event_id).execute()
        st.success(f"Event with ID {event_id} deleted successfully.")
    except Exception as e:
        st.error(f"An error occurred: {e}")

# Main Streamlit app
def main():
    st.title("Google Calendar Integration")

    # Authenticate with Google Calendar
    calendar = authenticate_google_calendar()

    # Add Event
    st.header("Add Event")
    event_name = st.text_input("Event Name")
    start_date_time = st.date_input("Start Date") + st.time_input("Start Time")
    length_hours = st.number_input("Duration (Hours)", min_value=1, max_value=24, value=1)

    if st.button("Add Event"):
        add_event(calendar, start_date_time, length_hours, event_name)

    # Get Events
    st.header("Get Events")
    from_date = st.date_input("From Date")
    to_date = st.date_input("To Date")
    if st.button("Get Events"):
        from_datetime = datetime.combine(from_date, datetime.min.time()).isoformat() + 'Z'
        to_datetime = datetime.combine(to_date, datetime.max.time()).isoformat() + 'Z'
        events = get_events(calendar, from_datetime, to_datetime)
        if events:
            for event in events:
                st.write(f"{event['summary']} - {event['start']['dateTime']}")
        else:
            st.write("No events found.")

    # Delete Event
    st.header("Delete Event")
    event_id = st.text_input("Event ID to Delete")
    if st.button("Delete Event"):
        delete_event(calendar, event_id)

if __name__ == "__main__":
    main()
