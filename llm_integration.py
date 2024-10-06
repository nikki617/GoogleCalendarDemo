# llm_integration.py

from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from langchain_core.tools import StructuredTool

# Define the argument classes for LangChain tools
class GetEventargs(BaseModel):
    from_datetime: datetime = Field(description="beginning of date range to retrieve events")
    to_datetime: datetime = Field(description="end of date range to retrieve events")

class AddEventargs(BaseModel):
    start_date_time: datetime = Field(description="start date and time of event")
    length_hours: int = Field(description="length of event")
    event_name: str = Field(description="name of the event")

# Create tools for LangChain agent
def create_tools(calendar):
    # Get events tool
    list_event_tool = StructuredTool(
        name="GetEvents",
        func=lambda from_datetime, to_datetime: get_events(calendar, from_datetime, to_datetime),
        args_schema=GetEventargs,
        description="Useful for getting the list of events from the user's calendar."
    )
    
    # Add event tool
    add_event_tool = StructuredTool(
        name="AddEvent",
        func=lambda start_date_time, length_hours, event_name: add_event(calendar, start_date_time, length_hours, event_name),
        args_schema=AddEventargs,
        description="Useful for adding an event with a start date, event name, and length in hours."
    )

    return [list_event_tool, add_event_tool]

# Create the LangChain agent
def create_llm_agent(tools):
    llm = ChatOpenAI(api_key=st.secrets["openai"]["api_key"], temperature=0.1)
    
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a helpful Google Calendar assistant"),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ]
    )
    
    agent = create_tool_calling_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools)
