# Multi-Tool Agent
 This multi-tool LLM Powered Assistant is capabable of accessing information through web searches, calculate basic mathematical operations, summarizing documents provided by the user and supports python code execution. 
## Set-Up:
Tools used to develop the system:
 - [Mistral AI API key](https://console.mistral.ai/apieys)
 - Python 3.10.11
 - LangChain 0.3.26
 - LangGraph 0.5.3
 - Gradio 5.37.0
 - langchain-tavily 0.2.9

Use the following commands to run the program:
``` bash
 pip install langchain
 pip install -U langgraph
 pip install --upgrade gradio
 pip install -qU "langchain[mistralai]"
 pip install -qU langchain-tavily
```