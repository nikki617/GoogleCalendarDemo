import streamlit as st
import datetime
from google.oauth2 import service_account
from calendar_integration import Calendar
from llm_integration import process_user_input

# Load the credentials directly from Streamlit secrets
credentials_info = st.secrets["CalendarAPI"]
calendar_id = 'nikki617@bu.edu'  # Replace with your actual calendar ID
timezone = 'America/New_York'  # Set your timezone

# Create the Calendar object
calendar_service = Calendar(credentials_info, calendar_id, timezone)

# Streamlit app title
st.title("Smart Meeting Scheduler with AI Integration")

# User input
user_input = st.text_input("You:", "")

if st.button("Send"):
    if user_input:
        response = process_user_input(user_input)  # Process user input through OpenAI
        
        # Check availability if the user asks for it
        if "show all events" in user_input.lower():
            start_date = datetime.datetime.now()
            end_date = start_date + datetime.timedelta(days=7)  # Next week
            events = calendar_service.get_calendar_events(start_date, end_date)
            if events:
                event_list = [
                    f"{event['summary']} from {event['start']} to {event['end']}" 
                    for event in events
                ]
                response += "\nYou have the following events scheduled:\n" + "\n".join(event_list)
            else:
                response += "\nYou're free for the next week!"
        
        st.write("Chatbot:", response)
    else:
        st.write("Please enter a message.")
