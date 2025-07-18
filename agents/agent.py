from logging import debug
import os
import getpass

from toolbox.calculator import Calculator
from toolbox.web_search import search_tool, news_search_tool, finance_search_tool
from toolbox.doc_reader import Doc_Reader

import langchain
import langgraph
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents.format_scratchpad.tools import (
    format_to_tool_messages,
)
from langchain.agents.output_parsers.tools import ToolsAgentOutputParser
from langchain.agents import create_tool_calling_agent
from mistralai import Mistral, UserMessage
from mistralai.models.chatcompletionrequest import ChatCompletionRequest

TAVILY = os.environ.get("MISTRAL_API_KEY")
MISTRAL = os.environ.get("TAVILY_API_KEY")

class Agent:
    def __init__(self, model="devstral small",llm=None, prompt_temp=None, temperature=0):
        self.model=model
        self.llm=llm
        self.temperature=temperature
        self.prompt_temp=prompt_temp
        self.tools = [Calculator, search_tool, news_search_tool, finance_search_tool]
    
    def set_llm(self):
        if not self.llm: 
            self.api_connect_check()
            self.llm = Mistral(api_key=MISTRAL)

    def set_prompt_template(self, prompt):
        self.prompt_temp = prompt
    
    def api_connect_check(self):
        if not MISTRAL:
            os.environ["MISTRAL_API_KEY"] = getpass.getpass("Enter API key for Mistral AI: ")
        if not TAVILY:
            os.environ["TAVILY_API_KEY"] = getpass.getpass("Enter API key for Tavily: ")



def create_agent():
    client = Agent()
    client.set_llm()
    debug(client.set_llm())
    response = client.llm.chat.stream(
    model=client.model,
    messages=[
        
        UserMessage(content="What is the capital of France?")
    ]
    )

    print(response.choices[0].message.content)
    # llm.set_prompt_template() 
    # return llm.construct_agent()

if __name__ == "__main__":
    create_agent()