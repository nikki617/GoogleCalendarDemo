# llm_integration.py

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.agents.react.agent import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
from calendar_integration import get_events, add_event
from calendar_integration import GetEventArgs, AddEventArgs


# Create the LLM
llm = ChatOpenAI(api_key="YOUR_OPENAI_API_KEY", temperature=0.1)

# Tool for getting events
get_event_tool = StructuredTool(
    name="GetEvents",
    func=get_events,
    args_schema=GetEventArgs,
    description="Useful for getting the list of events from the user's calendar."
)

# Tool for adding events
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
