# streamlit_app.py
import streamlit as st
from calendar_integration import setup_google_calendar_tools
from llm_integration import create_chatbot
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler
from langchain.callbacks.tracers import ConsoleCallbackHandler
from datetime import datetime, timedelta

# Streamlit app layout
st.set_page_config(page_title="Google Calendar Assistant", layout="wide")

# Initialize Google Calendar tools
tools, llm, agent, msgs = setup_google_calendar_tools()

# Create the chatbot agent
chatbot = create_chatbot(llm, tools)

# Layout for chat and calendar
col1, col2 = st.columns([1, 2])

# Left side for chat messages
with col1:
    st.sidebar.title("Chat")

    # User input for the chat
    if entered_prompt := st.sidebar.text_input("What does my day look like?", placeholder="Ask me about your schedule!"):
        # Clear the message history for the new prompt
        msgs.clear()

        st.sidebar.chat_message("human").write(entered_prompt)
        msgs.add_user_message(entered_prompt)

        # Get a response from the chatbot
        st_callback = StreamlitCallbackHandler(st.container())
        
        # Specify the default date range for the current week
        from_datetime = datetime.now()
        to_datetime = datetime.now() + timedelta(days=7)
        
        # Invoke the chatbot
        response = agent.invoke({"input": entered_prompt, "from_datetime": from_datetime, "to_datetime": to_datetime}, {"callbacks": [st_callback, ConsoleCallbackHandler()]})

        # Display only the AI's response, suppressing the details
        if 'output' in response:
            response_output = response["output"]
            st.sidebar.chat_message("ai").write(response_output)  # Show only AI response
            msgs.add_ai_message(response_output)

# Right side for calendar
with col2:
    st.subheader("Your Calendar")
    calendar_embed_code = """
    <iframe src="https://calendar.google.com/calendar/embed?src=nikki617%40bu.edu&ctz=Europe%2FBerlin" 
            style="border: 0" width="100%" height="650" frameborder="0" scrolling="no"></iframe>
    """
    st.components.v1.html(calendar_embed_code, height=650)
