import streamlit as st
import datetime
import json
from google.oauth2 import service_account
from gcsa.google_calendar import GoogleCalendar
from calendar_integration import authenticate_google_calendar, check_availability, book_event
from llm_integration import process_user_input

# Load the credentials from Streamlit secrets
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["CalendarAPI"],
    scopes=["https://www.googleapis.com/auth/calendar"]
)

# Create the GoogleCalendar object with the credentials
calendar_service = authenticate_google_calendar(credentials)

# Streamlit app title
st.title("Smart Meeting Scheduler with AI Integration")

# User input for chatbot interaction
user_input = st.text_input("You:", "")

# Button to send the input and process
if st.button("Send"):
    if user_input:
        # Process user input through OpenAI
        response = process_user_input(user_input)
        
        # Check availability if the user asks for it
        if "show all events" in user_input.lower():
            try:
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
            except Exception as e:
                response += f"\nError fetching events: {str(e)}"
        
        st.write("Chatbot:", response)
    else:
        st.write("Please enter a message.")
