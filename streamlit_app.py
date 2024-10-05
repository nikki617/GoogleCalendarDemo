# GPTCalendar.py
# Description: A chatbot that can organise your events for you!

from configs.config import OPENAI_API_KEY, PASSWORD, USERNAME, CALENDAR_URL, CREDENTIALS_FILE_PATH, TIMEZONE
import openai
import sys
import json
from openai_decorator import openaifunc, get_openai_funcs
import dateparser
from datetime import datetime, timedelta
from dateutil import parser
from Calendar import Calendar
import pytz

# Initialize OpenAI API key
openai.api_key = OPENAI_API_KEY

# Convert natural language dates to datetime objects
def convert_conversation_dates_to_datetime(natural_language_date):
    parsed_date = dateparser.parse(natural_language_date)
    if parsed_date:
        return parsed_date
    else:
        raise ValueError("Invalid date")


# Function to check calendar availability using the @openaifunc decorator
@openaifunc
def check_calendar(startDate: str = "now", endDate: str = "tomorrow"):
    """
    Check the calendar between two dates to see if the user is available or if they have anything planned.
    @param startDate: the start of the range
    @param endDate: the end of the range
    """
    credentials_file = CREDENTIALS_FILE_PATH
    timezone = TIMEZONE
    username = USERNAME

    start_range = convert_conversation_dates_to_datetime(startDate)
    end_range = start_range if startDate == endDate else convert_conversation_dates_to_datetime(endDate)

    calendar = Calendar(credentials_file, username, timezone)
    events = calendar.get_calendar_events(start_range, end_range)

    if not events:
        return "I'm free"

    return "I have " + ", ".join([f"{event['summary']} from {event['start']} to {event['end']}" for event in events])


# Function to book an event using the @openaifunc decorator
@openaifunc
def book_event(eventSummary: str = "AutoNamed", startDate: str = "NOT SET", endDate: str = "NOT SET", eventLocation: str = ""):
    """
    Book an event in the calendar if the user is free.
    @param eventSummary: a summary of the event
    @param startDate: the start of the range
    @param endDate: the end of the range
    @param eventLocation: the location where the event will be taking place
    """
    if startDate == "NOT SET" or endDate == "NOT SET":
        return "Please specify start and end dates."

    credentials_file = CREDENTIALS_FILE_PATH
    timezone = TIMEZONE
    username = USERNAME
    calendar = Calendar(credentials_file, username, timezone)

    # Check availability
    availability = check_calendar(startDate, endDate)
    if availability != "I'm free":
        return f"Sorry, I'm busy: {availability}"

    startDate = convert_conversation_dates_to_datetime(startDate)
    endDate = convert_conversation_dates_to_datetime(endDate)

    # Add the event
    calendar.add_event(eventSummary, startDate, endDate, eventLocation)

    return f"Great, your event '{eventSummary}' is booked from {startDate} to {endDate}."


# Function to edit an existing event using the @openaifunc decorator
@openaifunc
def edit_event(old_summary: str, old_start: str, old_end: str, old_location: str = "", new_summary: str = None, new_start: str = None, new_end: str = None, new_location: str = None):
    """
    Edit an existing calendar event.
    @param old_summary: the old summary of the event
    @param old_start: the old time the event started
    @param old_end: the old time the event ended
    @param old_location: the old location where the event was going to take place
    @param new_summary: an updated summary of the event
    @param new_start: the new time the event will start
    @param new_end: the new time the event will end
    @param new_location: the new location where the event will take place
    """
    credentials_file = CREDENTIALS_FILE_PATH
    timezone = TIMEZONE
    username = USERNAME
    calendar = Calendar(credentials_file, username, timezone)

    # Update event
    calendar.update_event(
        old_summary,
        convert_conversation_dates_to_datetime(old_start),
        convert_conversation_dates_to_datetime(old_end),
        old_location,
        new_summary,
        convert_conversation_dates_to_datetime(new_start) if new_start else None,
        convert_conversation_dates_to_datetime(new_end) if new_end else None,
        new_location
    )

    return f"Event '{old_summary}' has been updated."


# ChatGPT API Function to send a message
def send_message(message, messages):
    messages.append(message)
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",
            messages=messages,
            functions=get_openai_funcs(),
            function_call="auto",
        )
    except openai.error.AuthenticationError:
        print("AuthenticationError: Check your API-key")
        sys.exit(1)

    messages.append(response["choices"][0]["message"])
    return messages


# MAIN FUNCTION to run the conversation loop
def run_conversation(prompt, messages=[]):
    messages = send_message({"role": "user", "content": prompt}, messages)

    # Get response from ChatGPT
    message = messages[-1]

    while True:
        if message.get("function_call"):
            function_name = message["function_call"]["name"]
            arguments = json.loads(message["function_call"]["arguments"])

            # Execute the function
            function_response = globals()[function_name](**arguments)

            # Send function result to ChatGPT
            messages = send_message({"role": "function", "name": function_name, "content": function_response}, messages)
        else:
            print("ChatGPT: " + message["content"])
            user_message = input("You: ")
            messages = send_message({"role": "user", "content": user_message}, messages)

        message = messages[-1]


# ASK FOR PROMPT
print("I'm just a chatbot, but I can also organize your events for you!")
prompt = input("You: ")

# RUN CONVERSATION
run_conversation(prompt)
