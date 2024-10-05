# llm_integration.py

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.agents.react.agent import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
from calendar_integration import get_events, add_event, GetEventArgs  # Import GetEventArgs
from datetime import datetime  # Ensure this is imported too

# Create the LLM
llm = ChatOpenAI(api_key="YOUR_OPENAI_API_KEY", temperature=0.1)

# Tool for getting events
get_event_tool = StructuredTool(
    name="GetEvents",
    func=get_events,
    args_schema=GetEventArgs,  # Ensure GetEventArgs is used here
    description="Useful for getting the list of events from the user's calendar."
)

# Tool for adding events
class AddEventArgs(BaseModel):
    start_date_time: datetime = Field(description="start date and time of event")
    length_hours: int = Field(description="length of event")
    event_name: str = Field(description="name of the event")

add_event_tool = StructuredTool(
    name="AddEvent",
    func=add_event,
    args_schema=AddEventArgs,
    description="Useful for adding an event with a start date, event name, and length in hours."
)

# Function to get all tools
def get_tools():
    return [get_event_tool, add_event_tool]

# Messages used by the chatbot
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful Google Calendar assistant"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
)

# Create agent
def create_agent(tools):
    agent = create_tool_calling_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools)
