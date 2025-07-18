from ..agents.toolbox.tool_selector import ToolSelect
import operator
from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.messages import (
    BaseMessage,
    AIMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from typing import TypedDict, Annotated, List, Union, Dict, Any, Optional
from langgraph.graph.message import add_messages
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langgraph.graph import END, Graph
from langchain.agents import Tool
from langchain_core.memory import BaseMemory
from langchain_mistralai import ChatMistralAI


class Memory:
    def __init__(self, max_short_term=5, max_long_term=50):
        self.short_memory = []
        self.long_memory = []
        self.max_short_term = max_short_term
        self.max_long_term = max_long_term

    # Appending the message to long-term memory
    def append_long_term_memory(self, message: Dict[str, Any]):
        self.long_memory.append(message)
        if len(self.max_short_term) > self.max_short_term:
            self.memory.pop(0)
    
    # Appending the message to short-term memory
    def append_short_term_memory(self, message: Dict[str, Any]):
        self.short_memory.append(message)
        if len(self.max_short_term) > self.max_short_term:
            self.memory.pop(0)

    # Retrieving context from the recent conversation and key information about the conversation 
    def get_context(self):
        context = "Previous Conversation:\n"
        context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in self.short_memory[-5:]])
        
        if self.long_memory:
            context = "\n\nKey Info:\n"
            context = "\n".join([f"- {msg['content']}" for msg in self.long_memory[-3:]])

        return context            
    
    def importance_evaluator(self, data):
        prompt = """Rate the importance of remembering this information based on the overall conversation on a scale of 1-10:
        Text: "{data}"
        Respond only with a number."""
        response = ChatMistralAI.invoke(prompt)
        print(response)
        return int(response.content.strip()) >=7

    def update_memory(self, human_input: str, ai_output: str):
        self.append_short_term_memory({"role": "user", "content": human_input})
        self.append_short_term_memory({"role": "assistant", "content": ai_output})
        
        # Example heuristics for long-term memory (manual, delegated)
        if "remember this" or "record this" in human_input.lower():
            self.append_long_term_memory({"role": "user", "content": human_input})
            self.append_long_term_memory({"role": "assistant", "content": ai_output})
        elif self.importance_evaluator(human_input) == True:
            self.append_long_term_memory({"role": "user", "content": human_input})
            self.append_long_term_memory({"role": "assistant", "content": ai_output})

class AgentGraphState:
    def __init__(self):
        self.memory = Memory()
        self.history = list[BaseMessage]
        outcome: Union[AgentAction, AgentFinish, None]
        intermediate_steps: Annotated[list[tuple[AgentAction, str]], operator.add]
        self.pending_tool = None
        self.tool_result = None
    
    def update(self, user_input: str, ai_response: str = None, tool_name: str = None, tool_result: str = None):
        if user_input:
            self.memory.update_memory(user_input, ai_response or "")
        
        self.pending_tool = tool_name
        self.tool_result = tool_result
    
    def get_context(self) -> str:
        self.memory.get_context()
    
def build_workflow(tools: List[Tool], llm:ChatMistralAI):
    tool_selector = ToolSelect(tools)
    state=AgentGraphState()

    def receive_input
    def decide_action
    def tool_run
    def generate_response
    def decide_next_step
    def receive_input