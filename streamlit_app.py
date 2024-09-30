import streamlit as st
import json
import datetime
from google.oauth2 import service_account
from gcsa.google_calendar import GoogleCalendar
from calendar_integration import authenticate_google_calendar, check_availability, book_event, update_event, delete_event
from llm_integration import process_user_input

# Load the credentials from Streamlit secrets
credentials = service_account.Credentials.from_service_account_info(
    json.loads(st.secrets["CalendarAPI"]),
    scopes=["https://www.googleapis.com/auth/calendar"]
)

# Create the GoogleCalendar object with the credentials
calendar_service = authenticate_google_calendar(credentials)

# Streamlit app title
st.title("Smart Meeting Scheduler with AI Integration")

# User input
user_input = st.text_input("You:", "")

if st.button("Send"):
    if user_input:
        # Process user input through OpenAI
        response = process_user_input(user_input)

        # Check availability if the user asks for it
        if "check my calendar availability" in user_input.lower():
            start_date = datetime.datetime.now().isoformat() + 'Z'  # Current time
            end_date = (datetime.datetime.now() + datetime.timedelta(days=7)).isoformat() + 'Z'  # End next week
            events = check_availability(calendar_service, start_date, end_date)
            if events:
                event_list = [
                    f"{event['summary']} from {event['start'].get('dateTime', event['start'].get('date'))} to {event['end'].get('dateTime', event['end'].get('date'))}" 
                    for event in events
                ]
                response += "\nYou have the following events scheduled:\n" + "\n".join(event_list)
            else:
                response += "\nYou're free for the next week!"

        # Book an event
        elif "book a meeting" in user_input.lower():
            # Extract date and time from user_input (implement your own parsing logic here)
            start_time = (datetime.datetime.now() + datetime.timedelta(days=1)).isoformat() + 'Z'  # Placeholder
            end_time = (datetime.datetime.now() + datetime.timedelta(days=1, hours=1)).isoformat() + 'Z'  # Placeholder
            summary = "Meeting booked through AI"  # Placeholder summary
            event = book_event(calendar_service, start_time, end_time, summary)
            response += f"\nSure, I have booked a meeting for you on {start_time} to {end_time}. Anything else I can help with?"

        # Update an event
        elif "update the meeting" in user_input.lower():
            # Extract the event ID and new time (implement your own parsing logic here)
            event_id = "example_event_id"  # Placeholder for the actual event ID
            new_start_time = (datetime.datetime.now() + datetime.timedelta(days=1, hours=2)).isoformat() + 'Z'  # Placeholder
            new_end_time = (datetime.datetime.now() + datetime.timedelta(days=1, hours=3)).isoformat() + 'Z'  # Placeholder
            update_event(calendar_service, event_id, new_start_time, new_end_time)
            response += f"\nThe meeting has been updated to start at {new_start_time}. Anything else I can help with?"

        # Delete an event
        elif "delete the meeting" in user_input.lower():
            # Extract the event ID (implement your own parsing logic here)
            event_id = "example_event_id"  # Placeholder for the actual event ID
            delete_event(calendar_service, event_id)
            response += f"\nThe meeting has been deleted. Anything else I can help with?"

        st.write("Chatbot:", response)
    else:
        st.write("Please enter a message.")
