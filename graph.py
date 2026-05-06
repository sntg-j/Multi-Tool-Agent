import inspect
from tool_selector import ToolSelect
from agents.toolset.calculator import Calculator
from agents.toolset.web_search import search_tool, news_search_tool, finance_search_tool
from agents.toolset.doc_reader import Doc_Reader
from agents.memory import Memory  
from agents.agent import Agent, get_blank_client
from agents.role_prompts.prompt_templates import agent_template

from typing import List, Dict, Any, Optional, TypedDict 
from langgraph.graph import StateGraph

"""
    Graph Module Development Progress:
        As of 9/3/25
            - Isolated the issues for empty user inputs to memory bloating the 
                conversation history to the generate_response function.
            - Modified the data of the tool result and pending tool to include None 
                for improved conditional decisions in decide action function.
            - 
            - In the future, modify the general structure of the graph to improve the 
                readability of the module.
        
        Next steps:
            - continue the tool selection logic by including NLP functionality based on the user query
            - restructure the logger for each step of the graph
"""

tools = [Calculator, search_tool, news_search_tool, finance_search_tool, Doc_Reader]

class AgentState(TypedDict):
    """This class is used as an input schema template for the workflow.
        the variable names allow for proper data transfers from the invoke function's payload, 
        while the types define how the values are to be casted.
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

    def update(self, client: Agent, user_input: str = None, ai_response: str = None, tool_name: str = None, tool_result: str = None):
        if user_input != None:
            self.recent_input = user_input
            self.memory.update_memory(client, user_input)
            self.recent_input = None
    
        if ai_response != None:
            self.memory.append_short_term_memory({"role": "system", "content": ai_response})
            

        self.pending_tool = tool_name
        self.tool_result = tool_result

    def set_state(self, input: dict):
        if not isinstance(input["memory"], dict):
            input["memory"] = input["memory"].__dict__ # resets the data type format of the short and long term memories to avoid TypeErrors
        self.memory.short_memory = input["memory"]["short_memory"]
        self.memory.long_memory = input["memory"]["long_memory"]
        self.pending_tool = str(input["pending_tool"]) if input["pending_tool"] != None else None
        self.tool_result = str(input["tool_result"]) if input["pending_tool"] != None else None
        self.recent_input = input["recent_input"]
        self.debug = bool(input["debug"])

    def get_context(self) -> str:
        return self.memory.get_context()

##################################################################################################
#                                    DEBUGGING/LOGGING FUNCTIONS

def workflow_data(workflow: StateGraph):
    print("\nDEBUG MODE: SCHEMAS\n")
    print(f"State Schema:\t{workflow.state_schema.__dict__}\n")
    print(f"Input Schema:\t{workflow.input_schema.__dict__}\n")
    print(f"Output Schema:\t{workflow.output_schema.__dict__}\n")

def debug_graph(function_name: str = None, 
                input_data: dict = None,
                obj_form: AgentGraphState = None):
    args = list(locals().items()) # retrieving the parameters
    temp = locals()
    try:
    # tries using the list to sift through the types of data that comes into the function
    # this can make the function more flexible
        for key, param in args:
            if param == None: # if the parameter is empty
                temp.pop(key)
                if len(temp) == 0:
                    return f"Missing parameters on function call: {temp}"
            if isinstance(param, str):# function name is in use
                print(f"\n================{param}================\n")
            elif isinstance(param, dict): # input data from the user and ai response is in use
                # The purpose of this branch is to check the data type reading of the input at 
                # the start of each node in the graph workflow
                print("data type of memory:\t\t",type(param["memory"]))
                print("data type of short-term memory:\t",type(param["memory"]["short_memory"]))
                print("data type of long-term memory:\t",type(param["memory"]["long_memory"]))
                print("data type of pending_tool:\t",type(param["pending_tool"]))
                print("data type of tool_result:\t",type(param["tool_result"]))
                print("data type of recent_input:\t",type(param["recent_input"]))
            elif isinstance(param, AgentGraphState):# object data is in use
                # The purpose of this branch is to show the state of the data after
                # data manipulating operations within the workflow
                print("state_short_memory:\t",param.memory.short_memory)
                print("state_long_memory:\t",param.memory.long_memory)
                print("state_pending_tool:\t",param.pending_tool)
                print("state_tool_result:\t",param.tool_result)
                print("state_recent_input:\t",param.recent_input)
                print("state_debug:\t\t",param.debug)
        else: # this only happens if there is no parameter applicable to this is used
            return f"Unsupported parameter data type in {key}: {type(temp[key])}"
    except Exception as e:
        return f"Error: {str(e)}"

def debug_setup(obj: AgentGraphState, tool_selector: ToolSelect, input: dict):
    function_name = inspect.currentframe().f_code.co_name.upper()
    debug_graph(function_name=function_name)
    obj.memory.start_debug(bool(input["debug"]))
    tool_selector.set_debug(bool(input["debug"]))
    return

##################################################################################################

def build_workflow():
    client = get_blank_client()
    client.set_tools(tools)
    tool_selector = ToolSelect(tools)
    client.set_prompt_template(agent_template)

    # receives and processes input from the user
    def receive_input(input:dict)->dict:
        if bool(input["debug"]):
            print("\n================STARTING DEBUG MODE================\n")
            workflow_data(workflow)
            print("\nDEBUG MODE: SETUP\n")
    
        obj = AgentGraphState()
        obj.set_state(input)

        if bool(input["debug"]):
            function_name = inspect.currentframe().f_code.co_name.upper()
            debug_setup(obj, tool_selector, input)
            debug_graph(function_name, input)

        obj.update(client=client, user_input=obj.recent_input) # update with the user input data from the input referenced variable

        if bool(input["debug"]):
            debug_graph(obj_form=obj)

        return obj.__dict__ # does not change the inner object datatype when accessed...

    def decide_action(input:dict)->dict:
        if bool(input["debug"]):
            function_name = inspect.currentframe().f_code.co_name.upper()
            debug_graph(function_name, input)

        obj = AgentGraphState()
        obj.set_state(input)
        context = obj.get_context()

        if bool(input["debug"]):
            debug_graph(obj_form=obj)
            print(f"recent memory access through obj memory:\t{obj.memory.short_memory[-1]["content"]}") # accessing the most recent system response for any tools being called
        
        selected_tool = tool_selector.selection(obj.memory.short_memory[-1]["content"], context, client)
    
        if selected_tool != None:
            obj.update(client=client, tool_name=selected_tool.name)
        else:
            print("System response: This will be handled by the llm without tools.")

            # obj.update(client=client, ai_response="This will be handled by the llm without tools.")
        # in the event that our current toolbox cannot solve the user's question
        return obj.__dict__
    
    def tool_run(input:dict)->dict:
        if bool(input["debug"]):
            function_name = inspect.currentframe().f_code.co_name.upper()
            debug_graph(function_name, input)

        obj = AgentGraphState()
        obj.set_state(input)

        if bool(input["debug"]):
            debug_graph(obj_form=obj)
            temp = next(msg for msg in reversed(obj.memory.short_memory) if msg["role"] == "user")
            print(f"last user message access attempt:\t{temp}")
            print(f"result access attempt:\t{temp["content"]}\n")
            print(f"pending tool:\t{obj.pending_tool}")

        if obj.pending_tool != None:
            tool = tool_selector.tools[obj.pending_tool]

            # retrieves the most recent user message, to maintain state integrity
            last_user_msg = next( 
                msg for msg in reversed(obj.memory.short_memory) 
                if msg["role"] == "user"
            )

            result = tool.run(last_user_msg["content"])
            obj.update(client=client, tool_name=obj.pending_tool, tool_result=result)
        
        if bool(input["debug"]):
            print(f"pending tool: {obj.pending_tool}")
            print(f"tool result: {obj.tool_result}")
        return obj.__dict__
        
    
    def generate_response(input:dict)->dict:
        
        if bool(input["debug"]):
            function_name = inspect.currentframe().f_code.co_name.upper()
            debug_graph(function_name, input)
        
        obj = AgentGraphState()
        obj.set_state(input)
        context = obj.get_context()

        if bool(input["debug"]):
            debug_graph(obj_form=obj)
            print(f"context:\t{context}")
            print(f"short_memory access attempt:\t{obj.memory.short_memory[-1]["content"]}\n")

        chain = client.prompt_temp | client.llm
        response = chain.invoke({
            "context": context,
            "tools": [],
            "user_input": obj.memory.short_memory[-1]["content"]
        })

        if bool(input["debug"]):
            print(f"AI generated response:\t{response}")
            print(f"State in generated response:\t{obj.__dict__}")
        obj.update(client=client, ai_response=response)
        return{"response": response, "state": obj.__dict__}
    

    workflow = StateGraph(state_schema=AgentState, output_schema=AgentOutput)

    workflow.add_node("receive_input", receive_input)
    workflow.add_node("decide_action", decide_action)
    workflow.add_node("tool_run", tool_run)
    workflow.add_node("generate_response", generate_response)
    
    workflow.add_edge("receive_input", "decide_action")
    workflow.add_edge("tool_run", "generate_response")
    

    def workflow_router(input:dict)->str:
        if input["pending_tool"] != None or "None" != input["pending_tool"]:
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

