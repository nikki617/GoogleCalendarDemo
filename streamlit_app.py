import streamlit as st
import openai
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Load the OpenAI API key from secrets
openai.api_key = st.secrets["openai"]["api_key"]

# Load Google Calendar API credentials from secrets
calendar_credentials = {
    "type": st.secrets["CalendarAPI"]["type"],
    "project_id": st.secrets["CalendarAPI"]["project_id"],
    "private_key_id": st.secrets["CalendarAPI"]["private_key_id"],
    "private_key": st.secrets["CalendarAPI"]["private_key"].replace('\\n', '\n'),
    "client_email": st.secrets["CalendarAPI"]["client_email"],
    "client_id": st.secrets["CalendarAPI"]["client_id"],
    "auth_uri": st.secrets["CalendarAPI"]["auth_uri"],
    "token_uri": st.secrets["CalendarAPI"]["token_uri"],
    "auth_provider_x509_cert_url": st.secrets["CalendarAPI"]["auth_provider_x509_cert_url"],
    "client_x509_cert_url": st.secrets["CalendarAPI"]["client_x509_cert_url"]
}

# Set up the Google Calendar API client
credentials = service_account.Credentials.from_service_account_info(calendar_credentials)
scoped_credentials = credentials.with_scopes(['https://www.googleapis.com/auth/calendar.readonly'])
service = build('calendar', 'v3', credentials=scoped_credentials)

# Function to get OpenAI response
def get_openai_response(prompt):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=50
    )
    return response.choices[0].text.strip()

# Function to list Google Calendar events
def list_calendar_events(calendar_id='primary'):
    try:
        events_result = service.events().list(calendarId=calendar_id, maxResults=10).execute()
        events = events_result.get('items', [])
        if not events:
            return "No upcoming events found."
        event_list = []
        for event in events:
            event_list.append(event['summary'])
        return event_list
    except Exception as e:
        return f"An error occurred: {str(e)}"

# Streamlit app layout
st.title("AI-Powered Smart Meeting Scheduler")

# Input prompt for OpenAI
prompt = st.text_input("Ask me anything about your calendar:")
if prompt:
    response = get_openai_response(prompt)
    st.write(f"AI Response: {response}")

# Show calendar events
if st.button('Show me all events'):
    events = list_calendar_events()
    if isinstance(events, list):
        st.write("Upcoming events:")
        for event in events:
            st.write(f"- {event}")
    else:
        st.write(events)  # Display any error messages or no events message
