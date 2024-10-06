# llm_integration.py
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_tool_calling_agent, AgentExecutor
import streamlit as st

def setup_llm(tools):
    # Create the LLM
    llm = ChatOpenAI(api_key=st.secrets["openai"]["api_key"], temperature=0.1)

    # Chatbot prompt
    # In llm_integration.py
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful Google Calendar assistant. Always assume the user wants to see events for the year 2024 unless specified otherwise."),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
)


    # Create the agent
    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(
        agent=agent, 
        tools=tools,
    )
    
    return agent_executor
