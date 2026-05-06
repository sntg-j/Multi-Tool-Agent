import inspect
from graph import build_workflow
import gradio as gr
from langgraph.graph.state import CompiledStateGraph

DEBUG = True

class Wrapper:
    """
        Wrapping class for the chat history between users to the llm agent & model
        - The input of the wrapper function is a message string.
        - As such, the result needs to be a string for the ChatBot object to read 
            the information properly.
    """
    def __init__(self, workflow: CompiledStateGraph):
        self.workflow = workflow
        self.session_states = {}
        
    def __call__(self, message: str, session_id: str):
        if session_id not in self.session_states:
            self.session_states[session_id] = {
                "memory":{
                    "short_memory": [],
                    "long_memory": []
                },
                "pending_tool": None,
                "tool_result": None,
                "recent_input": message,
                "debug": DEBUG
            }
        else: # try resetting the values of the question and results to continue the conversation
            self.session_states[session_id]["recent_input"] = message
            self.session_states[session_id]["pending_tool"] = None
            self.session_states[session_id]["tool_result"] = None

        if DEBUG:
            function_name = inspect.currentframe().f_code.co_name.upper()
            print(f"\n================{function_name}_INPUT================")
            print(f"session_id: {session_id}")
            print(f"session_states: {self.session_states}\n")

        # peeks into the values key to allow proper data assignment, will not send anything otherwise.
        result = self.workflow.invoke(self.session_states["values"]) 

        if DEBUG:
            print(f"\n================{function_name}_OUTPUT================")
            print(f"Wrapper session states call:\t{self.session_states}\n")
            print(f"Wrapper result call:\t{result}\n")
            print(f"Wrapper result_state call:\t{result["state"]}\n")
            print(f"Wrapper result_response call:\t{result["response"]}\n")
        return result["response"]

agent_workflow = build_workflow()
wrapped_agent = Wrapper(agent_workflow)

with gr.Blocks(title="AI Agent") as demo:
    session_id = gr.Textbox(label="Session ID", value="values", visible=False)
    chatbot = gr.Chatbot(height=500)
    msg = gr.Textbox(label="Your Message")
    clear = gr.Button("Clear Chat")

    def respond(message, chat_history, session_id): # respond not returning ai response
        if len(chat_history) == 0:
            reset_state()

        if DEBUG:
            function_name = inspect.currentframe().f_code.co_name.upper()
            print(f"\n================{function_name.upper()}================")
            print(f"Pre-append history length:\t{len(chat_history)}")
            print(f"Outbound message:\t{len(message)}")

        agent_response = wrapped_agent(message, session_id)
        chat_history.append((message, agent_response))
        
        if DEBUG:
            print(f"Current history length:\t{len(chat_history)}\n")
        
        return "", chat_history
    
    def reset_state():
        wrapped_agent.session_states.clear() 
        wrapped_agent.session_states = {}
        if wrapped_agent.session_states.__len__() == 0 and DEBUG:
            function_name = inspect.currentframe().f_code.co_name.upper()
            print(f"\n================{function_name}================")
            print(f"session_states result:\t{wrapped_agent.session_states}")
            print("agent states cleared successfully...\n")

    msg.submit(
        respond,
        [msg, chatbot, session_id],
        [msg, chatbot]
    )
    clear.click(lambda: None, None, chatbot, queue=False)    

demo.launch()