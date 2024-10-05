# streamlit_app.py

import streamlit as st
from datetime import datetime, timedelta
from llm_integration import create_agent, create_llm, get_message_history
from calendar_integration import tools  # Ensure you import your tools here
from langchain_core.prompts import ChatPromptTemplate

# Create the LLM
llm = create_llm(st.secrets["openai"]["api_key"])

# Creating the prompt
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful Google Calendar assistant"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
)

# Create the agent with the required arguments
agent = create_agent(llm, tools, prompt)

# Initialize message history
msgs = get_message_history()

# Load the first AI message
if len(msgs.messages) == 0:
    msgs.add_ai_message("How may I assist you today?")

# Add the rest of the conversation
for msg in msgs.messages:
    if msg.type in ["ai", "human"]:
        st.chat_message(msg.type).write(msg.content)

# When the user enters a new prompt
if entered_prompt := st.chat_input("What does my day look like?"):
    # Add human message
    st.chat_message("human").write(entered_prompt)
    msgs.add_user_message(entered_prompt)

    # Specify the default date range for the current week
    from_datetime = datetime.now()
    to_datetime = datetime.now() + timedelta(days=7)

    # Invoke the agent with the entered prompt and the date range
    response = agent.invoke({"input": entered_prompt, "from_datetime": from_datetime, "to_datetime": to_datetime})

    # Check the response structure
    if "output" in response:
        output = response["output"]
        st.chat_message("ai").write(output)
        msgs.add_ai_message(output)
    else:
        # Handle the case where 'output' is not in the response
        error_message = "Sorry, I couldn't process your request. Please try again."
        st.chat_message("ai").write(error_message)
        msgs.add_ai_message(error_message)

