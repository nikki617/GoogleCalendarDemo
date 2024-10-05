# llm_integration.py

from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from calendar_integration import list_event_tool, add_event_tool

def create_agent():
    # Create the LLM
    llm = ChatOpenAI(api_key="YOUR_OPENAI_API_KEY", temperature=0.1)

    # Messages used by the chatbot
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a helpful Google Calendar assistant"),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ]
    )

    # Creating the agent that will integrate the provided calendar tool with the LLM.
    agent = create_tool_calling_agent(llm, [list_event_tool, add_event_tool], prompt)
    return AgentExecutor(agent=agent)
