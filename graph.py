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
    debug: bool

class AgentOutput(TypedDict):
    response: str
    state: Dict[str, Any]

class AgentGraphState:
    def __init__(self):
        self.memory = Memory()
        self.pending_tool = None
        self.tool_result = None
        self.recent_input = ""
        self.debug = None
    
    def update(self, client: Agent, user_input: str, ai_response: str, tool_name: str = None, tool_result: str = None):
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
        self.pending_tool = str(input["pending_tool"])
        self.tool_result = str(input["tool_result"])
        self.recent_input = input["recent_input"]
        self.debug = bool(input["debug"])
        self.memory.start_debug(self.debug)
        if self.debug:
            debug_mode("SET_STATE", self)

    def get_context(self) -> str:
        return self.memory.get_context()

def debug_mode(node_name: str, state: AgentGraphState):
    print(f"\n========================{node_name.upper()}===============================")
    print("state_short_memory:\t",state.memory.short_memory)
    print("state_long_memory:\t",state.memory.long_memory)
    print("state_pending_tool:\t",state.pending_tool)
    print("state_tool_result:\t",state.tool_result)
    print("state_recent_input:\t",state.recent_input)
    print("state_debug:\t\t",state.debug)
    print("")

def build_workflow():
    client = get_blank_client()
    client.set_tools(tools)
    tool_selector = ToolSelect(tools)
    client.set_prompt_template(agent_template)

    # receives and processes input from the user
    def receive_input(input:dict)->dict:
        if not isinstance(input["memory"], dict):
            input["memory"] = input["memory"].__dict__

        if bool(input["debug"]):
            print("\n================STARTING DEBUG MODE================\n")
            print("\nDEBUG MODE: SCHEMAS\n")
            print(f"State Schema:\t{workflow.state_schema.__dict__}\n")
            print(f"Input Schema:\t{workflow.input_schema.__dict__}\n")
            print(f"Output Schema:\t{workflow.output_schema.__dict__}\n")
            print("\nDEBUG MODE: SETUP\n")
            tool_selector.set_debug(bool(input["debug"]))
        
        obj = AgentGraphState()
        
        if bool(input["debug"]):
            print("\n================RECEIVE_INPUT================\n")

        obj.set_state(input)
        obj.update(client=client, user_input=obj.recent_input, ai_response="") # update with the user input data from the input referenced variable
        
        if bool(input["debug"]):
            print("post-update obj vals:\t",obj.__dict__)
        
        return obj.__dict__
    
    def decide_action(input:dict)->dict:
        if not isinstance(input["memory"], dict):
            input["memory"] = input["memory"].__dict__ # resets the data type format of the short and long term memories to avoid TypeErrors

        if bool(input["debug"]):
            print("\n================DECIDE_ACTION================\n")
            print("Modified memory received:\t", input["memory"])
        
        obj = AgentGraphState()
        obj.set_state(input)
        context = obj.get_context()

        if obj.debug:
            print(f"recent memory access:\t{obj.memory.short_memory[-1]["content"]}") # accessing the most recent system response for any tools being called

        selected_tool = tool_selector.selection(obj.memory.short_memory[-1]["content"], context, client)
        
        if selected_tool:
            return {"tool": selected_tool.name}
        
        # in the event that our current toolbox is not enough to solve the user's question
        return {"response": "This will be handled by the llm without tools"} 

    def tool_run(input:dict)->dict:
        if not isinstance(input["memory"], dict):
            input["memory"] = input["memory"].__dict__ # resets the data type format of the short and long term memories to avoid TypeErrors

        if bool(input["debug"]):
            print("\n================TOOL_RUN================\n")
        
        obj = AgentGraphState()
        obj.set_state(input)
        tool = tool_selector.tools[obj.pending_tool]

        if obj.debug:
            temp = next(msg for msg in reversed(obj.memory.short_memory) if msg["role"] == "user")
            print(f"last user message access attempt:\t{temp}")
            print(f"result access attempt:\t{temp["content"]}\n")

        # retrieves the most recent user message, to maintain state integrity
        last_user_msg = next( 
            msg for msg in reversed(obj.memory.short_memory) 
            if msg["role"] == "user"
        )

        result = tool.run(last_user_msg["content"])
        obj.update(client=client, user_input="", ai_response="", tool_name=obj.pending_tool, tool_result=result)
        return obj.__dict__
    
    def generate_response(input:dict)->dict:
        if not isinstance(input["memory"], dict):
            input["memory"] = input["memory"].__dict__ # resets the data type format of the short and long term memories to avoid TypeErrors

        if bool(input["debug"]):
            print("\n================GENERATE_RESPONSE================\n")
        
        obj = AgentGraphState()
        obj.set_state(input)
        context = obj.get_context()

        if obj.debug:
            debug_mode("generate_respone", obj)
            print(f"context:\t{context}")
            print(f"short_memory access attempt:\t{obj.memory.short_memory[-1]["content"]}\n")

        chain = client.prompt_temp | client.llm
        response = chain.invoke({
            "context": context,
            "tools": [],
            "user_input": obj.memory.short_memory[-1]["content"]
        })

        if obj.debug:
            print(f"AI generated response:\t{response}")
            print(f"State in generated response:\t{obj.__dict__}")
        obj.update(client=client, user_input="", ai_response=response)
        return{"response": response, "state": obj.__dict__}
    
    workflow = StateGraph(state_schema=AgentState, output_schema=AgentOutput)

    
    workflow.add_node("receive_input", receive_input)
    workflow.add_node("decide_action", decide_action)
    workflow.add_node("tool_run", tool_run)
    workflow.add_node("generate_response", generate_response)
    
    workflow.add_edge("receive_input", "decide_action")
    workflow.add_edge("tool_run", "generate_response")

    def workflow_router(input:dict)->str:
        if "tool" in input:
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

