import streamlit as st
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import AIMessage, HumanMessage, SystemMessage

# Initialize the ChatOpenAI with your API key from Streamlit secrets
chat = ChatOpenAI(
    temperature=0,
    model='gpt-3.5-turbo',
    openai_api_key=st.secrets["openai"]["api_key"]  # Ensure this is set correctly in secrets
)

def process_user_input(user_input):
    messages = [
        SystemMessage(content='You are an assistant that helps manage calendar events.'),
        HumanMessage(content=user_input)
    ]

    # Generate AI response
    ai_response = chat(messages=messages).content
    return ai_response
