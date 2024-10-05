# llm_integration.py

from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_community.chat_message_histories import StreamlitChatMessageHistory

class LangChainManager:
    def __init__(self, api_key):
        self.llm = ChatOpenAI(api_key=api_key, temperature=0.1)
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "You are a helpful Google Calendar assistant"),
                ("human", "{input}"),
                ("placeholder", "{agent_scratchpad}"),
            ]
        )

    def create_agent(self, tools):
        agent = create_tool_calling_agent(self.llm, tools, self.prompt)
        return AgentExecutor(agent=agent, tools=tools)

    def load_message_history(self):
        return StreamlitChatMessageHistory(key="special_app_key")
