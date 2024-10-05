from gcsa.event import Event
from gcsa.google_calendar import GoogleCalendar
from google.oauth2 import service_account
import json
import streamlit as st

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI
from langchain.agents import create_tool_calling_agent
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

## Google Calendar Setup

# Get the credentials from Streamlit secrets
credentials = service_account.Credentials.from_service_account_info(
    json.loads(st.secrets["CalendarAPI"]),
    scopes=["https://www.googleapis.com/auth/calendar"]
)

# Create the Google Calendar instance
calendar = GoogleCalendar(credentials=credentials)

# Define the tool to get calendar events
def get_events_tool(dummy):
    return list(calendar.get_events(calendar_id="mndhamod@gmail.com"))

# Create a Tool object for the events tool
event_tool = Tool(
    name="GetEvents",
    func=get_events_tool,
    description="Useful for getting the list of events from the user's calendar."
)

# List of tools (you can add more as needed)
tools = [event_tool]

# LangChain - Set up the LLM
llm = ChatOpenAI(api_key=st.secrets["openai"]["api_key"], temperature=0.5)

# Create the agent executor using LangChain's agent framework
agent_executor = create_tool_calling_agent(llm, tools)

# Set up chat history in Streamlit
msgs = StreamlitChatMessageHistory(key="special_app_key")

if len(msgs.messages) == 0:
    msgs.add_ai_message("How can I help you?")

# Define the chat prompt structure
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are an AI chatbot having a conversation with a human."),
        ("history", "You are retaining the user's chat history for context."),
        ("human", "{question}"),
    ]
)

# A chain that takes the prompt and processes it through the agent (LLM + tools)
chain = prompt | agent_executor

# Queries the LLM with full chat history using RunnableWithMessageHistory
chain_with_history = RunnableWithMessageHistory(
    chain,
    lambda session_id: msgs,  # Return the previously created chat history instance
    input_messages_key="question",
    history_messages_key="history",
)

# Streamlit UI for the chatbot interface
for msg in msgs.messages:
    if msg.type in ["ai", "human"]:
        st.chat_message(msg.type).write(msg.content)

# Handling user input
if user_input := st.chat_input():
    # Add human message to chat history
    msgs.add_human_message(user_input)
    st.chat_message("human").write(user_input)

    # Run the LLM agent with chat history
    response = chain_with_history.invoke({"question": user_input})

    # Add the AI's response to the chat history
    ai_response = response["messages"][-1].content
    msgs.add_ai_message(ai_response)
    st.chat_message("ai").write(ai_response)
