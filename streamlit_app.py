# Required Imports
from gcsa.event import Event
from gcsa.google_calendar import GoogleCalendar
from google.oauth2 import service_account
from datetime import datetime, timedelta
from langchain_core.tools import StructuredTool
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler
from pydantic import BaseModel, Field
import streamlit as st

# Google Calendar Credentials
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["CalendarAPI"],
    scopes=["https://www.googleapis.com/auth/calendar"]
)

# Create the GoogleCalendar instance
calendar = GoogleCalendar(credentials=credentials)

# Event listing tool
class GetEventargs(BaseModel):
    from_datetime: datetime = Field(description="beginning of date range to retrieve events")
    to_datetime: datetime = Field(description="end of date range to retrieve events")

def get_events(from_datetime, to_datetime):
    current_year = datetime.now().year
    from_datetime = from_datetime.replace(year=current_year)
    to_datetime = to_datetime.replace(year=current_year)
    
    events = calendar.get_events(calendar_id="nikki617@bu.edu", time_min=from_datetime, time_max=to_datetime)
    return list(events)

list_event_tool = StructuredTool(
    name="GetEvents",
    func=get_events,
    args_schema=GetEventargs,
    description="Useful for getting the list of events from the user's calendar."
)

# Event adding tool
class AddEventargs(BaseModel):
    start_date_time: datetime = Field(description="start date and time of event")
    length_hours: int = Field(description="length of event")
    event_name: str = Field(description="name of the event")

def add_event(start_date_time, length_hours, event_name):
    current_year = datetime.now().year
    start_date_time = start_date_time.replace(year=current_year)
    start = start_date_time
    end = start + timedelta(hours=length_hours)
    event = Event(event_name, start=start, end=end)
    return calendar.add_event(event, calendar_id="nikki617@bu.edu")

add_event_tool = StructuredTool(
    name="AddEvent",
    func=add_event,
    args_schema=AddEventargs,
    description="Useful for adding an event with a start date, event name, and length in hours."
)

tools = [list_event_tool, add_event_tool]

# Create the LLM
llm = ChatOpenAI(api_key=st.secrets["openai"]["api_key"], temperature=0.1)

# Chatbot prompt
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful Google Calendar assistant"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
)

# Create the agent
agent = create_tool_calling_agent(llm, tools, prompt)
agent = AgentExecutor(agent=agent, tools=tools)

# Storing message history
msgs = StreamlitChatMessageHistory(key="special_app_key")

# Streamlit app layout
st.set_page_config(page_title="Google Calendar Assistant", layout="wide")
st.title("🗓️ Google Calendar Assistant")

# CSS for styling
st.markdown(
    """
    <style>
    .chat-container {
        max-height: 400px;
        overflow-y: auto;
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 20px;
    }
    .user-message {
        background-color: #e1f5fe;
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 5px;
    }
    .ai-message {
        background-color: #ffe0b2;
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 5px;
    }
    </style>
    """, unsafe_allow_html=True
)

# Layout for chat and calendar
col1, col2 = st.columns([1, 1])

# Left side for the chat interface
with col1:
    st.subheader("Chat with Your Assistant")
    chat_container = st.container()

    # Message input field
    entered_prompt = st.text_input("Ask your Google Calendar Assistant:", "")

    if st.button("Send"):
        # Clear the message history for the new prompt
        msgs.clear()

        if entered_prompt:
            st.chat_message("human").write(entered_prompt)
            msgs.add_user_message(entered_prompt)

            # Get a response from the agent
            st_callback = StreamlitCallbackHandler(chat_container)
            
            # Specify the default date range for the current week
            from_datetime = datetime.now()
            to_datetime = datetime.now() + timedelta(days=7)
            
            # Invoke the agent
            response = agent.invoke({"input": entered_prompt, "from_datetime": from_datetime, "to_datetime": to_datetime}, {"callbacks": [st_callback]})

            # Add AI response
            response = response["output"]
            st.chat_message("ai").write(response)
            msgs.add_ai_message(response)

# Right side for the calendar
with col2:
    # Embed the Google Calendar
    calendar_embed_code = """
    <iframe src="https://calendar.google.com/calendar/embed?src=nikki617%40bu.edu&ctz=Europe%2FBerlin" 
            style="border: 0" width="100%" height="600" frameborder="0" scrolling="no"></iframe>
    """
    st.components.v1.html(calendar_embed_code, height=600)
