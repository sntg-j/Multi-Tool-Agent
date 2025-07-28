import os
import getpass
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import OpenAI
from typing_extensions import override

OPENAI = os.environ.get("OPEN_AI_KEY")
TAVILY = os.environ.get("TAVILY_API_KEY")

class Agent:
    """The purpose of this class, is not to override any other Langchain method, but to consolidate the 
        components of that allow functionality in the Agent Worflow.
        
        model = determines the model of the llm in the agent object. set to gpt-3.5-turbo-instruct by default
        llm = the connection to OpenAI's API server for prompt generation.
        prompt_temp = serves as a template for the agent to formulate their responses.
        temperature = the level of randomness the llm has in generating each response. (AKA sampling temperature)
        """
    def __init__(self, model="gpt-3.5-turbo-instruct",llm=None, prompt_temp=None, temperature=0):
        self.model=model
        self.llm=llm
        self.temperature=temperature
        self.prompt_temp=prompt_temp
        self.tools = None
    
    # works similarly to bind tools, but is just managed by the tool selection logic
    def set_tools(self, tools):
        self.tools = tools

    # starts up the API connection with OpenAI
    def set_llm(self):
        if not self.llm: 
            self.api_connect_check()
            self.llm = OpenAI(api_key=OPENAI, temperature=self.temperature)
    
    # shortens the length of call, whlie applying the same method in the base class
    def invoke(self, prompt):
        return self.llm.invoke(prompt)

    def set_prompt_template(self, prompt):
        self.prompt_temp = ChatPromptTemplate.from_messages([
            ("assistant", prompt),("human","{user_input}")])

    def api_connect_check(self):
        # Will continue asking until the API key is entered properly
        while not OPENAI: 
            os.environ["OPEN_AI_KEY"] = getpass.getpass("Enter API key for OpenAI: ")
        while not TAVILY:
            os.environ["TAVILY_API_KEY"] = getpass.getpass("Enter API key for Tavily: ")


def get_blank_client():
    client = Agent()
    client.set_llm()
    return client