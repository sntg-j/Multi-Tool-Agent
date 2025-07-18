import os
import getpass
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import OpenAI

OPENAI = os.environ.get("OPEN_AI_KEY")
TAVILY = os.environ.get("TAVILY_API_KEY")

class Agent:
    def __init__(self, model="gpt-3.5-turbo-instruct",llm=None, prompt_temp=None, temperature=0):
        self.model=model
        self.llm=llm
        self.temperature=temperature
        self.prompt_temp=prompt_temp
        self.tools = None
    
    def set_tools(self, tools):
        self.tools = tools

    def set_llm(self):
        if not self.llm: 
            self.api_connect_check()
            self.llm = OpenAI(api_key=OPENAI)

    def set_prompt_template(self, prompt):
        self.prompt_temp = ChatPromptTemplate.from_messages([
            ("system", prompt),("human","{user_input}")])

    def api_connect_check(self):
        if not OPENAI:
            os.environ["OPEN_AI_KEY"] = getpass.getpass("Enter API key for OpenAI: ")
        if not TAVILY:
            os.environ["TAVILY_API_KEY"] = getpass.getpass("Enter API key for Tavily: ")


def get_blank_client():
    client = Agent()
    client.set_llm()
    return client

# Test function for arbitrary agent creation and API calls
# def create_agent():
#     client = Agent()
#     # client.set_llm()
#     client.set_llm()
#     client.set_prompt_template(agent_template) 
#     # response = client.llm.invoke(
#     #     input=""
#     # )
#     # print(response)
#     return client
