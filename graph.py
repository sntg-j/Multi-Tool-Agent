from tool_selector import ToolSelect
from agents.agent import Agent, get_blank_client
from prompts.prompt_templates import agent_template
from typing import List, Dict, Any, Optional, TypedDict 
from langgraph.graph import StateGraph
from langchain.agents import Tool


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
    
    def importance_evaluator(self, client: Agent, data: Dict[str, Any]):
        prompt = """Rate the importance of remembering this information based on the overall conversation on a scale of 1-10:
        Text: "{data}"
        Respond only with a number."""
        response = client.llm.invoke(prompt)
        return int(response) >=7

    def update_memory(self, client:Agent, human_input: str, ai_output: str):
        self.append_short_term_memory({"role": "user", "content": human_input})
        self.append_short_term_memory({"role": "assistant", "content": ai_output})
        
        # Example heuristics for long-term memory (manual, delegated)
        if "remember this" or "record this" in human_input.lower():
            self.append_long_term_memory({"role": "user", "content": human_input})
            self.append_long_term_memory({"role": "assistant", "content": ai_output})
        elif self.importance_evaluator(client, human_input) == True:
            self.append_long_term_memory({"role": "user", "content": human_input})
            self.append_long_term_memory({"role": "assistant", "content": ai_output})

class AgentState(TypedDict):
    memory: Memory
    pending_tool: Optional[str]
    tool_result: Optional[str]
    last_input: str

class AgentGraphState:
    def __init__(self):
        self.memory = Memory()
        self.pending_tool = None
        self.tool_result = None
        self.recent_input = ""
    
    def update(self, client: Agent, user_input: str, ai_response: str = None, tool_name: str = None, tool_result: str = None):
        if user_input:
            self.recent_input = user_input
            self.memory.update_memory(user_input, ai_response or "", client=client)
        
        if ai_response:
            self.memory.append_short_term_memory({"role": "assistant", "content": ai_response})

        self.pending_tool = tool_name
        self.tool_result = tool_result
    
    def get_context(self) -> str:
        self.memory.get_context()
    
def build_workflow(tools: List[Tool]):
    client = get_blank_client()
    client.set_tools(tools)
    tool_selector = ToolSelect(tools)
    client.set_prompt_template(agent_template)


    # receives and processes input from the user
    def receive_input(state: dict, user_input: str):
        obj = AgentGraphState()
        obj.__dict__ = state
        obj.update(client, user_input)
        return obj.__dict__
    
    def decide_action(state: dict):
        obj = AgentGraphState()
        obj.__dict__ = state
        context = obj.get_context()

        selected_tool = tool_selector.selection(obj.memory.short_memory[-1]["content"], context)
        
        if selected_tool:
            return {"tool": selected_tool.name}
        
        # in the event that our current toolbox is not enough to solve the user's question
        return {"response": "This will be handled by the llm without tools"} 

    def tool_run(state:dict):
        obj = AgentGraphState()
        obj.__dict__= state
        tool = tool_selector.tools[obj.pending_tool]
            
        # retrieves the most recent user message, to maintain state integrity
        last_user_msg = next( 
            msg for msg in reversed(obj.memory.short_memory) 
            if msg["role"] == "user"
        )

        result = tool.run(last_user_msg["content"])
        obj.update(None, tool_name=obj.pending_tool, tool_result=result, client=client)
        return obj.__dict__
    
    def generate_response(state:dict):
        obj = AgentGraphState()
        obj.__dict__ = state
        context = obj.get_context()

        chain = client.prompt_temp | client.llm
        response = chain.invoke({
            "input": obj.memory.short_memory[-1]["content"]
        })

        obj.update(None, response, client=client)
        return{"response": response, "state": obj.__dict__}
    
    workflow = StateGraph(AgentState)

    workflow.add_node("receive_input", receive_input)
    workflow.add_node("decide_action", decide_action)
    workflow.add_node("tool_run", tool_run)
    workflow.add_node("generate_response", generate_response)
    
    workflow.add_edge("receive_input", "decide_action")
    workflow.add_edge("tool_run", "generate_response")

    def workflow_router(state: dict):
        if "tool" in state:
            return "tool_run"
        return "generate_response"

    workflow.add_conditional_edges(
        "decide_action",
        workflow_router,
        {
            "tool_run": "tool_run",
            "generate_response": "generate_response"
        }
    )

    workflow.set_entry_point("receive_input")
    workflow.set_finish_point("generate_response")

    return workflow.compile()
