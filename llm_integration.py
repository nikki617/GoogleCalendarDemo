# llm_integration.py

from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_openai import ChatOpenAI
from calendar_integration import list_event_tool, add_event_tool
from langchain_core.prompts import ChatPromptTemplate

# Create the LLM
llm = ChatOpenAI(api_key=st.secrets["openai"]["api_key"], temperature=0.1)

# Messages used by the chatbot
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful Google Calendar assistant."),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
)

# Initialize the tools as instances of Tool or StructuredTool
tools = [
    Tool(
        name=list_event_tool['name'],
        func=list_event_tool['func'],
        description=list_event_tool['description'],
        parameters=list_event_tool['parameters']
    ),
    Tool(
        name=add_event_tool['name'],
        func=add_event_tool['func'],
        description=add_event_tool['description'],
        parameters=add_event_tool['parameters']
    ),
]

# Creating the agent that will integrate the provided calendar tool with the LLM
agent = create_tool_calling_agent(llm, tools, prompt)

# Create the AgentExecutor
agent_executor = AgentExecutor(agent=agent, tools=tools)
