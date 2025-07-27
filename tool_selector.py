from typing import Optional, List
from langchain_core.tools import Tool

from agents.agent import Agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda

class ToolSelect:
    def __init__(self, tools: List[Tool], debug = False):
        self.tools = {tool.name: tool for tool in tools}
        self._last_selected = None  # Track last selection to prevent loops
        self.debug = debug
    
    def set_debug(self, mode: bool):
        print("Changing ToolSelect to debug mode...")
        self.debug = mode
        print(f"debug mode: {self.debug}")
        return

    def selection(self, query: str, context: str, client: Agent) -> Optional[Tool]:
        query = query.lower()  # case normalization
        for name, tool in self.tools.items():
            if self.debug:
                print(f"current tool name:\t{name}")
            if name.lower() in query:
                if self.debug:
                    print(f"explicitly calling tool:\t{name}")
                return tool
        
        for tool in self.tools.values():
            keywords = tool.description.lower().split()[:5]
            if self.debug:
                print(f"keyword used:\t{keywords}")
            if any(kw in query for kw in keywords if len(kw) > 3):  # Skip short words
                if self.debug:
                    print(f"tool found by deciding keyword:\t{keywords}")
                return tool
            
        if self._last_selected != query:  # Prevent infinite loops
            if self.debug:
                print(f"query:\t{query}")
                print(f"last selected tool:\t{self._last_selected}")
            self._last_selected = query
            return self.llm_delegation(query, context, client)
        return None
    
    def llm_delegation(self, query: str, context: str, client: Agent) -> Optional[Tool]:
        prompt = ChatPromptTemplate.from_messages([
            ("system", 
             "Select the most appropriate tool for this task. "
             "Consider both the user query and conversation context.\n"
             "Context:\n{context}\n\n"
             "Guidelines:\n"
             "1. Choose only from the available tools\n"
             "2. Respond with exactly the tool name or 'None'\n"
             "3. Prioritize tools that match the query precisely"),
            ("human", 
             "Query: {query}\n\n"
             "Available Tools:\n{tools}\n\n"
             "Tool Name:")
        ])
        tools_list = "\n".join(
            f"{i}. {name}: {tool.description}" 
            for i, (name, tool) in enumerate(self.tools.items(), 1)
        )
        chain = (
            prompt 
            | client.llm.bind(stop=["\n"])  # Stop at newline to get just the name
            | RunnableLambda(lambda x: self.tools.get(x.content.strip(), None))
        )
        
        try:
            if self.debug:
                print("==========LLM DELEGATION==========")
                print(f"tool list:\t{tools_list}")
                print(f"chain:\t{chain.__dict__}")
                print(f"prompt\t{prompt}\n")
            return chain.invoke({
                "query": query,
                "context": context,
                "tools": tools_list
            })
        except Exception:
            return None  # Fail gracefully

