from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import StructuredTool
from langchain.callbacks.tracers import ConsoleCallbackHandler
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler
from pydantic import BaseModel, Field
from datetime import datetime
import streamlit as st

from calendar_integration import get_events, add_event, cancel_event, reschedule_event, GetEventargs, AddEventargs, CancelEventargs, RescheduleEventargs

# Create Tool objects for calendar integration
list_event_tool = StructuredTool(
    name="GetEvents",
    func=get_events,
    args_schema=GetEventargs,
    description="Useful for getting the list of events from the user's calendar."
)

add_event_tool = StructuredTool(
    name="AddEvent",
    func=add_event,
    args_schema=AddEventargs,
    description="Useful for adding an event with a start date, event name, and length in hours."
)

cancel_event_tool = StructuredTool(
    name="CancelEvent",
    func=cancel_event,
    args_schema=CancelEventargs,
    description="Useful for canceling an event with a specific name within a date range."
)

# LLM setup
def create_llm_agent():
    llm = ChatOpenAI(api_key=st.secrets["openai"]["api_key"], temperature=0.1)
    
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a helpful Google Calendar assistant"),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ]
    )

    tools = [list_event_tool, add_event_tool, cancel_event_tool, reschedule_event_tool]  # Add reschedule_event_tool

    agent = create_tool_calling_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools)

# Function to invoke the agent and return the response
def invoke_agent(agent, prompt, from_datetime, to_datetime):
    st_callback = StreamlitCallbackHandler(st.container())
    response = agent.invoke(
        {"input": prompt, "from_datetime": from_datetime, "to_datetime": to_datetime}, 
        {"callbacks": [st_callback, ConsoleCallbackHandler()]}
    )
    return response["output"]
