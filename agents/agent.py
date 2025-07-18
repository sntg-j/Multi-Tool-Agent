import os
import getpass

from ..agents.toolbox.calculator import Calculator
from .toolbox.web_search import search_tool, news_search_tool, finance_search_tool

import langchain
import langgraph
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents.format_scratchpad.tools import (
    format_to_tool_messages,
)
from langchain.agents.output_parsers.tools import ToolsAgentOutputParser
from langchain.agents import create_tool_calling_agent
from langchain_mistralai import ChatMistralAI

TAVILY = os.environ.get("MISTRAL_API_KEY")
MISTRAL = os.environ.get("TAVILY_API_KEY")


# def prompt_template(): 
#     prompt = ChatPromptTemplate.from_messages(
#         [
#             {
#                 "system",
#                 # """You are a multi-tool agent with a variety of purposes. You have calculator funcionality,
#                 # code execution support, web search, and document/pdf summarization capabilities.""",
#                 """You are a multi-tool agent with a variety of purposes. You have calculator funcionality""",
#             },
#             MessagesPlaceholder(variable_name="chat_history"),
#             {"user", "{content}"},
#             MessagesPlaceholder(variable_name="agent_scratchpad"),
#         ]
#     )
#     return prompt

class Agent:
    def __init__(self, model, prompt_temp=None, temperature=0, ):
        self.model=model
        self.temperature=temperature
        self.prompt_temp=prompt_temp
        self.tools = [Calculator, search_tool, news_search_tool, finance_search_tool]
    
    def set_llm(self):
        if not self.model: 
            self.api_connect_check()
            self.model = ChatMistralAI(model_name="mistral-large-latest", api_key=MISTRAL, model_provider="mistralai")

    def set_prompt_template(self, prompt:str):
        self.prompt_temp = prompt
    
    def construct_agent(self):
        self.model.bind_tools(self.tools)
        return create_tool_calling_agent(self.model, tools=None, prompt=self.prompt_temp)

    def api_connect_check(self):
        if not MISTRAL:
            os.environ["MISTRAL_API_KEY"] = getpass.getpass("Enter API key for Mistral AI: ")
        if not TAVILY:
            os.environ["TAVILY_API_KEY"] = getpass.getpass("Enter API key for Tavily: ")

def create_agent():
    llm = Agent()
    llm.set_llm()
    llm.set_prompt_template()

    return llm.construct_agent()
    
    