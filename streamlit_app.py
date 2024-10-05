import streamlit as st
import openai
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Load the OpenAI API key from the secrets
openai.api_key = st.secrets["openai"]["api_key"]

# Load Google Calendar API credentials from the secrets
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
service = build('calendar', 'v3', credentials=credentials)

# Example of making an OpenAI API call
def get_openai_response(prompt):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=50
    )
    return response.choices[0].text.strip()

# Example of interacting with Google Calendar
def list_calendar_events(calendar_id='primary'):
    events_result = service.events().list(calendarId=calendar_id, maxResults=10).execute()
    events = events_result.get('items', [])
    if not events:
        st.write('No upcoming events found.')
    for event in events:
        st.write(event['summary'])

# Example usage
st.title("Smart Meeting Scheduler with AI Integration")

prompt = st.text_input("Enter your prompt for OpenAI:")
if prompt:
    response = get_openai_response(prompt)
    st.write(f"AI Response: {response}")

if st.button('List Calendar Events'):
    list_calendar_events()

