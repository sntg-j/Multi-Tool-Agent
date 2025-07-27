# Multi-Tool Agent
 This multi-tool LLM Powered Assistant is capabable of accessing information through web searches, calculate basic mathematical operations, summarizing documents provided by the user and supports python code execution. 
## Set-Up:
Tools used to develop the system:
 - [Opent AI key](https://platform.openai.com/settings/organization/api-keys)
 - Python 3.12.1
 - LangChain 0.3.26
 - LangGraph 0.5.3
 - Gradio 5.37.0
 - langchain-tavily 0.2.9
 - PyMuPDF 1.26.3
 - pip install openai
 - pip install -qU langchain-openai

Use the following commands to run the program:
``` bash
 pip install -r requirements.txt
 ```

 ## Video Demonstration:
 I was unable to upload the video on Youtube, so I will be sharing it as a link to the Google Drive file in the link below:
 [Demonstration Video](https://drive.google.com/file/d/1c3kafFqY9SQCqcWiDJNjVmaMbh5TwS1r/view?usp=sharing)

 ## Additional Info about AI Agents
 Components of an AI (LLM powered) Agent:
 - Memory/State Management

    - This maintains context and history of steps across the length of the chat and queries. From recent interactions for Short Term Memory to storing facts, documents, or past events for recall for long term memory.

 - Tools & Tool Selection Logic 
    - Allows the agent to take actions such as calling APIs, running code, searching the web, or conducting mathematical operations.
    - This can be the Tool Abstraction in LangChain or LangGraph.

 - Prompting Template
    - Determines how the LLM is to behave like an agent using prompting engineering.

 - LLM Core
    - This can be any model used to power the reasnoning and decision-making aspects of the agent.

 - Input/Output Interfaces
    - Input: Accepts the input from the user (i.e. a query, task or observation.)
    - Output: Delivers the agent's response back to the user or system.
       - This process is done through Chat UIs, API communication, etc.

### Structure of my architecture: