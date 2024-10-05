import openai
import streamlit as st

# Access API key from Streamlit secrets
openai.api_key = st.secrets["openai"]["api_key"]

# Main Streamlit app logic
st.title("Smart Meeting Scheduler")

st.write("Let's use OpenAI API!")

# Example usage of OpenAI API for chat completion
try:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # or gpt-4 if you have access
        messages=[
            {"role": "user", "content": "What is the current weather?"}
        ]
    )
    # Display the response
    st.write(response.choices[0].message['content'])
except Exception as e:
    st.error(f"Error: {e}")
