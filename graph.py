from tool_selector import ToolSelect
from agents.toolset.calculator import Calculator
from agents.toolset.web_search import search_tool, news_search_tool, finance_search_tool
from agents.toolset.doc_reader import Doc_Reader
from agents.memory import Memory  
from agents.agent import Agent, get_blank_client
from agents.role_prompts.prompt_templates import agent_template

from typing import List, Dict, Any, Optional, TypedDict 
from langgraph.graph import StateGraph


tools = [Calculator, search_tool, news_search_tool, finance_search_tool, Doc_Reader]

class AgentState(TypedDict):
    """This class is used as a input schema template for the workflow's input.
        the variable names allow the proper data transfers from the invoke function's payload, 
        while the types are how the values are to be casted.
        """
    memory: Dict[str, Any]
    pending_tool: Optional[str]
    tool_result: Optional[str]
    recent_input: Dict[str, str]
    debug: str

class AgentGraphState:
    def __init__(self):
        self.memory = Memory()
        self.pending_tool = None
        self.tool_result = None
        self.recent_input = ""
        self.debug = None
    
    def update(self, client: Agent, user_input: str, ai_response: str = None, tool_name: str = None, tool_result: str = None):
        if user_input:
            self.recent_input = user_input
            self.memory.update_memory(client, user_input, ai_response or "")
        
        if ai_response:
            self.memory.append_short_term_memory({"role": "system", "content": ai_response})

        self.pending_tool = tool_name
        self.tool_result = tool_result
    
    def set_state(self, input: dict):
        self.memory.short_memory = input["memory"]["short_memory"]
        self.memory.long_memory = input["memory"]["long_memory"]
        self.pending_tool = input["pending_tool"]
        self.tool_result = input["tool_result"]
        self.recent_input = input["recent_input"]
        self.debug = input["debug"]

    def get_context(self) -> str:
        return self.memory.get_context()

def debug_mode(node_name: str, state: AgentGraphState):
    print(f"\n========================{node_name.capitalize()}===============================")
    print("state_short_memory: ",state.memory.short_memory)
    print("state_long_memory: ",state.memory.long_memory)
    print("state_pending_tool: ",state.pending_tool)
    print("state_tool_result: ",state.tool_result)
    print("state_recent_input: ",state.recent_input)
    print("state_debug: ",state.debug)
    print("")

def build_workflow():
    client = get_blank_client()
    client.set_tools(tools)
    tool_selector = ToolSelect(tools)
    client.set_prompt_template(agent_template)

    # receives and processes input from the user
    def receive_input(input:dict):        
        obj = AgentGraphState()

        obj.set_state(input)
        obj.update(client, user_input=obj.recent_input) # update with the user input data from the input referenced variable
        
        if obj.debug:
            print("\n================STARTING DEBUG MODE================\n")
            print("\nDEBUG MODE: STATE_SCHEMA\n")
            print(workflow.state_schema.__dict__)
            print("\nDEBUG MODE: SETUP\n")
            tool_selector.set_debug(obj.debug)
            debug_mode("receive_input", obj)

        # return obj.__dict__
    
    def decide_action(input: dict):
        obj = AgentGraphState()
        obj.set_state(input)
        context = obj.get_context()

        if obj.debug:
            debug_mode("decide_action", obj)

        selected_tool = tool_selector.selection(obj.memory.short_memory[-1]["content"], context, client)
        
        if selected_tool:
            return {"tool": selected_tool.name}
        
        # in the event that our current toolbox is not enough to solve the user's question
        return {"response": "This will be handled by the llm without tools"} 

    def tool_run(input:dict):
        obj = AgentGraphState()
        obj.set_state(input)
        tool = tool_selector.tools[obj.pending_tool]

        if obj.debug:
            debug_mode("tool_run", obj)
        # retrieves the most recent user message, to maintain state integrity
        last_user_msg = next( 
            msg for msg in reversed(obj.memory.short_memory) 
            if msg["role"] == "user"
        )

        result = tool.run(last_user_msg["content"])
        obj.update(None, tool_name=obj.pending_tool, tool_result=result, client=client)
        return obj.__dict__
    
    def generate_response(input:dict):
        obj = AgentGraphState()
        obj.set_state(input)
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

