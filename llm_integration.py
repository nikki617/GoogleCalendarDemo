# llm_integration.py

# Required imports
from langchain.agents import create_tool_calling_agent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_core.callbacks import CallbackManager
from langchain.callbacks.tracers import ConsoleCallbackHandler

# Create the LLM
def create_llm(api_key):
    """
    Creates an instance of the ChatOpenAI model with the given API key.
    
    Args:
        api_key (str): The OpenAI API key.
        
    Returns:
        ChatOpenAI: An instance of the ChatOpenAI model.
    """
    return ChatOpenAI(api_key=api_key, temperature=0.1)

# Create the agent
def create_agent(llm, tools, prompt):
    """
    Creates an agent that integrates the LLM with the provided tools and prompt.
    
    Args:
        llm (ChatOpenAI): The language model.
        tools (list): A list of tools to be used by the agent.
        prompt (ChatPromptTemplate): The prompt template to be used.
        
    Returns:
        AgentExecutor: An agent executor that can be used to process inputs.
    """
    agent = create_tool_calling_agent(llm, tools, prompt)
    return agent

# Storing message history
def get_message_history(key="special_app_key"):
    """
    Creates a message history object for Streamlit.
    
    Args:
        key (str): The key used for storing message history.
        
    Returns:
        StreamlitChatMessageHistory: The message history object.
    """
    return StreamlitChatMessageHistory(key=key)
