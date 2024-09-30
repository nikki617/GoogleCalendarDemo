# llm_integration.py

from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate

# Load the OpenAI API key from Streamlit secrets
def load_openai_key():
    import streamlit as st
    return st.secrets["openai"]["api_key"]

openai_api_key = load_openai_key()

# Initialize the chat model
chat = ChatOpenAI(
    temperature=0,
    model='gpt-3.5-turbo',
    openai_api_key=openai_api_key  # Ensure this is set correctly
)

def process_user_input(user_input):
    response = chat([{"role": "user", "content": user_input}])
    return response['choices'][0]['message']['content']
