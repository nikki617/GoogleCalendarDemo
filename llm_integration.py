# llm_integration.py

from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents.react.agent import create_react_agent
from langchain_core.output_parsers import StrOutputParser
from langchain_core.tools import Tool, StructuredTool
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor

# Import the calendar functions
from calendar_integration import get_events, add_event

# Create the LLM
def create_agent(api_key):
    llm = ChatOpenAI(api_key=api_key, temperature=0.1)

    # Messages used by the chatbot
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a helpful Google Calendar assistant"),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ]
    )

    # Creating the agent that will integrate the provided calendar tool with the LLM.
    agent = create_tool_calling_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools)

# Create tools (make sure to import StructuredTool from langchain_core.tools)
def get_tools():
    from calendar_integration import get_events, add_event  # Import functions here

    # Create Tool objects for events
    list_event_tool = StructuredTool(
        name="GetEvents",
        func=get_events,
        args_schema=GetEventArgs,
        description="Useful for getting the list of events from the user's calendar."
    )

    add_event_tool = StructuredTool(
        name="AddEvent",
        func=add_event,
        args_schema=AddEventArgs,
        description="Useful for adding an event with a start date, event name, and length in hours."
    )

    return [list_event_tool, add_event_tool]
