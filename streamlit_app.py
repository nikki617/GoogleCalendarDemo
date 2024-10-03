import streamlit as st
import datetime
from google.oauth2 import service_account
from openai_decorator import openaifunc, get_openai_funcs
from calendar_integration import authenticate_google_calendar, check_availability, book_event

# Load credentials for calendar API
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["CalendarAPI"],
    scopes=["https://www.googleapis.com/auth/calendar"]
)
calendar_service = authenticate_google_calendar(credentials)
calendar_id = "your-calendar-id@example.com"

# Streamlit app UI
st.title("AI-Powered Smart Meeting Scheduler")

# User input
user_input = st.text_input("Ask me anything about your calendar:", "")

# OpenAI interaction
if st.button("Submit"):
    from llm_integration import process_user_input

    if user_input:
        # Process user input via OpenAI
        response = process_user_input(user_input)

        # Handle calendar actions (OpenAI API function integration)
        if "check calendar" in user_input.lower():
            start_date = datetime.datetime.now().isoformat() + 'Z'
            end_date = (datetime.datetime.now() + datetime.timedelta(days=7)).isoformat() + 'Z'
            try:
                events = check_availability(calendar_service, start_date, end_date)
                if events:
                    event_list = [f"{event['summary']} from {event['start']} to {event['end']}" for event in events]
                    response += "\nYou have the following events scheduled:\n" + "\n".join(event_list)
                else:
                    response += "\nYou're free for the next week!"
            except Exception as e:
                response += f"\nAn error occurred: {e}"
        
        st.write("Response:", response)
