import streamlit as st
import openai

class LLMIntegration:
    def __init__(self):
        openai.api_key = st.secrets['openai']['api_key']

    def generate_response(self, prompt):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response['choices'][0]['message']['content']
        except Exception as e:
            st.error(f"Error communicating with OpenAI: {e}")
            return None
