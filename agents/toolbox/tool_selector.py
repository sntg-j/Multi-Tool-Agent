from calculator import Calculator
from web_search import finance_search_tool, news_search_tool, search_tool
from typing import List, Dict, Any, Optional
from langchain_core.tools import Tool


from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from typing import List, Dict, Any, Optional
from langchain_core.memory import BaseMemory
from mistralai.models.agentscompletionrequest import AgentsCompletionRequestToolChoice
from mistralai.client import MistralClient

class ToolSelect:
    def __init__(self, tools:list[Tool]):
        self.tools={tool.name: tool for tool in tools}
    
    def selection(self, query: str, context:str) -> Optional[Tool]:
        query = query.lower()
        for tool_name, tool in self.tools.items():
            if any(keyword in query.lower for keyword in tool.description.lower().split()[:]):
                return tool
            return self.llm_delegation(query, context)
    
    def llm_delegation(self,client: MistralClient, query:str, context: str) -> Optional[Tool]:
        response = client.chat(
            model="mistral-large-latest",
            messages=[{"role": "user", "content": query}],
            tools=self.tools,
            AgentsCompletionRequestToolChoice = "auto"  # Let model decide
        )
        # return
        response.choices[0].message.tool_calls[0]

