from calculator import Calculator
from web_search import finance_search_tool, news_search_tool, search_tool
from typing import List, Dict, Any, Optional
from langchain_core.tools import Tool

from agent import get_blank_client
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from typing import List, Dict, Any, Optional
from langchain_core.memory import BaseMemory

class ToolSelect:
    def __init__(self, tools:list[Tool]):
        self.tools={tool.name: tool for tool in tools}
    
    def selection(self, query: str, context:str) -> Optional[Tool]:
        query = query.lower() # normalizing the query words to allow proper tool calls
        for tool_name, tool in self.tools.items():
            if any(keyword in query.lower for keyword in tool.description.lower().split()[:]):
                return tool
            return self.llm_delegation(query, context)
    
    def llm_delegation(self, query:str, context: str, client=get_blank_client()) -> Optional[Tool]:
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Select the best tool for the user's query. Context:\n{context}"),
            ("human", "Query: {query}\n\nAvailable Tools:\n{tools}\n\nRespond only with the tool name or 'None'.")
        ])
        chain = prompt | client.llm | RunnableLambda(
            lambda x:self.tools.get(x.content.strip(), None)
        )
        tools_list = "\n".join([f"- {name}: {tool.description}" for name, tool in self.tools.items()])

        return chain.invoke({
            "query": query,
            "context": context,
            "tools": tools_list
        })

