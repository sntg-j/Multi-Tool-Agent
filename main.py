from typing import Any, Dict, List
import gradio as gr
from graph import build_workflow
from agents.toolset.calculator import Calculator
from agents.toolset.web_search import search_tool, news_search_tool, finance_search_tool
from agents.toolset.doc_reader import Doc_Reader
from graph import Memory

tools = [Calculator,search_tool, news_search_tool, finance_search_tool,Doc_Reader]

class Wrapper:
    def __init__(self, workflow):
        self.workflow = workflow
        self.session_states = {}
        
    def __call__(self, message: str, session_id: str):
        if session_id not in self.session_states:
            self.session_states[session_id] = {
                "memory": Memory(),
                "pending_tool": None,
                "tool_result": None,
                "last_input": ""
            }

        result = self.workflow.invoke({
            "state": self.session_states[session_id],
            "user_input": message  # Ensure this is passed correctly
        })

        self.session_states[session_id] = result.get("state", {})
        return result["response"]
        

agent_workflow = build_workflow(tools=tools)
wrapped_agent = Wrapper(agent_workflow)

with gr.Blocks(title="AI Agent") as demo:
    session_id = gr.Textbox(label="Session ID", value="default", visible=False)
    chatbot = gr.Chatbot(height=500)
    msg = gr.Textbox(label="Your Message")
    clear = gr.Button("Clear Chat")

    def respond(message, chat_history, session_id):
        agent_response = wrapped_agent(message, session_id)
        chat_history.append((message, agent_response))
        return "", chat_history

    msg.submit(
        respond,
        [msg, chatbot, session_id],
        [msg, chatbot]
    )
    clear.click(lambda: None, None, chatbot, queue=False)

demo.launch()


# def chat(message):
#     history = []
#     agent = build_workflow()
#     response = agent.message
#     history.append(response)
#     # return response



# if __name__ == "__main__":

#     demo = gr.ChatInterface(chat)
#     demo.launch()