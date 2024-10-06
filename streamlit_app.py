
import streamlit as st
from calendar_integration import setup_google_calendar_tools
from llm_integration import setup_llm
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler
from langchain.callbacks.tracers import ConsoleCallbackHandler
from datetime import datetime

# Set up tools and LLM
tools, calendar = setup_google_calendar_tools()
agent_executor = setup_llm(tools)

# Storing message history
msgs = StreamlitChatMessageHistory(key="special_app_key")

# Streamlit app layout
st.set_page_config(page_title="Google Calendar Assistant", layout="wide")

# Layout for chat and calendar
col1, col2 = st.columns([1, 2])

# Left side for chat messages
with col1:
    st.sidebar.title("Chat")

    if entered_prompt := st.sidebar.text_input("What does my day look like?", placeholder="Ask me about your schedule!"):
        # Clear the message history for the new prompt
        msgs.clear()
        st.sidebar.chat_message("human").write(entered_prompt)
        msgs.add_user_message(entered_prompt)

        # Get a response from the agent
        st_callback = StreamlitCallbackHandler(st.container())

        # Specify the date range for the entire year of 2024
        from_datetime = datetime(2024, 1, 1)
        to_datetime = datetime(2024, 12, 31)

        # Invoke the agent
        response = agent_executor.invoke({"input": entered_prompt, "from_datetime": from_datetime, "to_datetime": to_datetime}, {"callbacks": [st_callback, ConsoleCallbackHandler()]})

        # Display only the AI's response, suppressing the details
        if 'output' in response:
            response_output = response["output"]
            st.sidebar.chat_message("ai").write(response_output)
            msgs.add_ai_message(response_output)

# Right side for calendar
with col2:
    st.subheader("Your Calendar")
    calendar_embed_code = """
    <iframe src="https://calendar.google.com/calendar/embed?src=nikki617%40bu.edu&ctz=Europe%2FBerlin" 
            style="border: 0" width="100%" height="650" frameborder="0" scrolling="no"></iframe>
    """
    st.components.v1.html(calendar_embed_code, height=650)
