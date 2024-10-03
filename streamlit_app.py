import streamlit as st
import json
from google.oauth2 import service_account
from gcsa.google_calendar import GoogleCalendar
from calendar_integration import authenticate_google_calendar, check_availability, book_event, delete_event, update_event
from llm_integration import process_user_input
import datetime

# Load the credentials directly from Streamlit secrets
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["CalendarAPI"],
    scopes=["https://www.googleapis.com/auth/calendar"]
)

# Authenticate the Google Calendar
calendar_service = authenticate_google_calendar(credentials)

# Streamlit app title
st.title("Smart Meeting Scheduler with AI Integration")

# Display the calendar events
calendar_id = "nikki617@bu.edu"  # Your calendar ID
st.write("Events from your Google Calendar:")

try:
    # Fetch all events for the next 7 days
    now = datetime.datetime.utcnow()
    start_date = now.isoformat() + 'Z'  # Current time in UTC
    end_date = (now + datetime.timedelta(days=7)).isoformat() + 'Z'  # End next week
    events = check_availability(calendar_service, start_date, end_date)

    if events:
        for event in events:
            st.write(f"**Event:** {event.summary}")
            st.write(f"**Start:** {event.start.isoformat()}")
            st.write(f"**End:** {event.end.isoformat()}")
            st.write("---")
    else:
        st.write("No events found.")
except Exception as e:
    st.error(f"An error occurred while fetching events: {e}")

# User input
user_input = st.text_input("You:", "")

if st.button("Send"):
    if user_input:
        response = process_user_input(user_input)  # Process user input through OpenAI

        if "events" in user_input.lower():  # Check for events request
            try:
                events = check_availability(calendar_service, start_date, end_date)  # Use updated function
                if events:
                    event_list = [
                        f"{event.summary} from {event.start.isoformat()} to {event.end.isoformat()}" 
                        for event in events
                    ]
                    response += "\nYou have the following events:\n" + "\n".join(event_list)
                else:
                    response += "\nYou have no events for the next week!"
            except Exception as e:
                response += f"\nAn error occurred while fetching your events: {e}"

        st.write("Chatbot:", response)
    else:
        st.write("Please enter a message.")
