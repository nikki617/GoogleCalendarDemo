import streamlit as st
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from datetime import datetime, timedelta
from llm_integration import process_user_input  # Import your AI processing function

# Load the credentials from Streamlit secrets
credentials = service_account.Credentials.from_service_account_info(
    json.loads(st.secrets["CalendarAPI"]),
    scopes=["https://www.googleapis.com/auth/calendar"]
)

# Create the Google Calendar service instance
def create_calendar_service(credentials):
    return build('calendar', 'v3', credentials=credentials)

# Function to check availability
def check_availability(service, start_date, end_date):
    events_result = service.events().list(
        calendarId='primary',
        timeMin=start_date,
        timeMax=end_date,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    return events_result.get('items', [])

# Main function
def main():
    st.title("Smart Meeting Scheduler with AI Integration")

    # Create a Google Calendar service instance
    service = create_calendar_service(credentials)

    # User input for interaction
    user_input = st.text_input("You:", "")
    
    if st.button("Send"):
        if user_input:
            response = process_user_input(user_input)  # Process user input through OpenAI

            # Check availability if the user asks for it
            if "show all events" in user_input.lower():
                start_date = datetime.now().isoformat() + 'Z'  # Current time
                end_date = (datetime.now() + timedelta(days=7)).isoformat() + 'Z'  # End next week
                events = check_availability(service, start_date, end_date)
                if events:
                    event_list = [
                        f"{event['summary']} from {event['start'].get('dateTime', event['start'].get('date'))} to {event['end'].get('dateTime', event['end'].get('date'))}" 
                        for event in events
                    ]
                    response += "\nYou have the following events scheduled:\n" + "\n".join(event_list)
                else:
                    response += "\nYou're free for the next week!"

            st.write("Chatbot:", response)
        else:
            st.write("Please enter a message.")

if __name__ == "__main__":
    main()
