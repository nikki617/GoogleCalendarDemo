# llm_integration.py
import streamlit as st
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import AIMessage, HumanMessage, SystemMessage

# Access the API key correctly
openai_api_key = st.secrets["openai"]["api_key"] if "openai" in st.secrets else None
if openai_api_key is None:
    raise ValueError("OpenAI API key not found in secrets.")

# Initialize the ChatOpenAI with your API key
chat = ChatOpenAI(
    temperature=0,
    model='gpt-3.5-turbo',
    openai_api_key=openai_api_key  # Ensure this is set correctly in secrets
)

def process_user_input(user_input):
    messages = [
        SystemMessage(content='You are an assistant that helps manage calendar events.'),
        HumanMessage(content=user_input)
    ]

    # Generate AI response
    ai_response = chat(messages=messages).content
    return ai_response
