import gradio as gr
from graph import build_workflow
from langgraph.graph.state import CompiledStateGraph

DEBUG = True

class Wrapper:
    # Wrapping class to structure the input method of each chat message from users to the llm agent & model
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

        # peeks into the values key to allow proper data assignment, will not send anything otherwise.
        result = self.workflow.invoke(self.session_states["values"]) 


        # self.session_states[session_id] = result.get("state", {})
        self.session_states[session_id] = result
        return result["response"]

agent_workflow = build_workflow()
wrapped_agent = Wrapper(agent_workflow)

with gr.Blocks(title="AI Agent") as demo:
    session_id = gr.Textbox(label="Session ID", value="values", visible=False)
    chatbot = gr.Chatbot(height=500)
    msg = gr.Textbox(label="Your Message")
    clear = gr.Button("Clear Chat")

    def respond(message, chat_history, session_id):
        agent_response = wrapped_agent(message, session_id)
        if DEBUG:
            print(f"Pre-append history length:\t{len(chat_history)}")
        chat_history.append((message, agent_response))
        if DEBUG:
            print(f"Current history length:\t{len(chat_history)}")
        return "", chat_history

    msg.submit(
        respond,
        [msg, chatbot, session_id],
        [msg, chatbot]
    )
    clear.click(lambda: None, None, chatbot, queue=False)

demo.launch()