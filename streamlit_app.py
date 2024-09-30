import streamlit as st
import json
from google.oauth2 import service_account
from gcsa.google_calendar import GoogleCalendar
from calendar_integration import authenticate_google_calendar, check_availability, book_event  # Import from your module
from llm_integration import process_user_input
import datetime
import re  # Import regex for date parsing

# Load the credentials directly from Streamlit secrets without json.loads
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["CalendarAPI"],
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
        response = process_user_input(user_input)  # Process user input through OpenAI
        
        # Check availability if the user asks for it
        if "check my calendar availability" in user_input.lower():
            # Extract date range from user input (assuming input format is clear)
            match = re.search(r'from (.*?) to (.*?)$', user_input, re.IGNORECASE)
            if match:
                start_date = match.group(1).strip()
                end_date = match.group(2).strip()

                # Convert the dates to the required format
                try:
                    start_datetime = datetime.datetime.strptime(start_date, "%B %d").replace(year=datetime.datetime.now().year)
                    end_datetime = datetime.datetime.strptime(end_date, "%B %d").replace(year=datetime.datetime.now().year)

                    # Ensure the end date is after the start date
                    if end_datetime < start_datetime:
                        response += "\nThe end date must be after the start date."
                    else:
                        start_iso = start_datetime.isoformat() + 'Z'
                        end_iso = end_datetime.isoformat() + 'Z'

                        events = check_availability(calendar_service, start_iso, end_iso)
                        if events:
                            event_list = [
                                f"{event['summary']} from {event['start'].get('dateTime', event['start'].get('date'))} to {event['end'].get('dateTime', event['end'].get('date'))}"
                                for event in events
                            ]
                            response += "\nYou have the following events scheduled:\n" + "\n".join(event_list)
                        else:
                            response += "\nYou're free during that period!"
                except ValueError:
                    response += "\nPlease enter the dates in the correct format (e.g., 'September 30' to 'October 7')."

        st.write("Chatbot:", response)
    else:
        st.write("Please enter a message.")
