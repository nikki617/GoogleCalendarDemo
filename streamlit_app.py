import streamlit as st
from datetime import datetime, timedelta
from calendar_integration import CalendarIntegration
import openai
import os

# Load secrets
secrets = st.secrets['google']
openai.api_key = st.secrets['openai']['api_key']

calendar_service = CalendarIntegration()

def check_availability():
    start_date = datetime.now() + timedelta(days=1)  # Start from tomorrow
    end_date = start_date + timedelta(days=7)  # Next week
    events = calendar_service.get_calendar_events(start_date, end_date)
    
    if events:
        return "\n".join([f"{event['summary']} from {event['start']} to {event['end']}" for event in events])
    else:
        return "You're free for the next week!"

st.title("Smart Meeting Scheduler with AI Integration")
user_input = st.text_input("You:", "")

if user_input:
    if "check my calendar availability" in user_input.lower():
        response = check_availability()
    else:
        response = "I'm sorry, but I don't have access to your calendar. You can check your availability by looking at your calendar app or scheduling tool. If you need help with scheduling, let me know!"

    st.text_area("Chatbot:", response, height=150)
