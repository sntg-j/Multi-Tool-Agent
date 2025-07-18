from agents.agent import create_agent
import gradio as gr

def chat(message, history):
    pass
    # agent = create_agent()
    # response = agent.run(message)
    # return response

demo = gr.ChatInterface(chat)
demo.launch()