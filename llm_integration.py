# llm_integration.py
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
import streamlit as st

def create_chatbot(llm, tools):
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

    return agent, msgs
