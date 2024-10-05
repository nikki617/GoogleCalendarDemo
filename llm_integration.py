# Create the LLM
llm = ChatOpenAI(api_key=st.secrets["openai"]["api_key"], temperature=0.1)

# Messages used by the chatbot
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful Google Calendar assistant"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
)

# Creating the agent that will integrate the provided calendar tool with the LLM.
agent = create_tool_calling_agent(llm, tools, prompt)
agent = AgentExecutor(
    agent=agent, 
    tools=tools,
)

#--------------------

# Storing message history
msgs = StreamlitChatMessageHistory(key="special_app_key")

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

    # Get a response from the agent
    st_callback = StreamlitCallbackHandler(st.container())
    
    # Specify the default date range for the current week
    from_datetime = datetime.now()
    to_datetime = datetime.now() + timedelta(days=7)
    
    # Invoke the agent with the entered prompt and the date range
    response = agent.invoke({"input": entered_prompt, "from_datetime": from_datetime, "to_datetime": to_datetime}, {"callbacks": [st_callback, ConsoleCallbackHandler()]})

    # Add AI response
    response = response["output"]
    st.chat_message("ai").write(response)
    msgs.add_ai_message(response)
