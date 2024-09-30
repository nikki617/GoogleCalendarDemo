# streamlit_app.py

import streamlit as st
from calendar_integration import authenticate_google_calendar, check_av
from llm_integration import process_user_input

# Load the credentials from Streamlit secrets
calendar = authenticate_google_calendar()

st.title("Smart Meeting Scheduler")

# Health Check Endpoint
if st.button("Health Check"):
    st.write("Service is running!")

# User input for scheduling
user_input = st.text_input("Ask me about scheduling a meeting:")
if user_input:
    response = process_user_input(user_input)
    st.write(f"Response: {response}")

# Check availability
if st.button("Check Availability"):
    start_time = st.date_input("Start Date")
    end_time = st.date_input("End Date")
    
    events = check_av(calendar, start_time, end_time)
    if events:
        st.write("Available events:")
        for event in events:
            st.write(event)
    else:
        st.write("No events found in this time frame.")
