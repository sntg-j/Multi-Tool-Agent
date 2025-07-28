from agents.agent import Agent
from typing import List, Dict, Any, Optional, TypedDict 

class Memory:
    def __init__(self, max_short_term=5, max_long_term=50, debug=False):
        self.short_memory = []
        self.long_memory = []
        self.max_short_term = max_short_term
        self.max_long_term = max_long_term
        self.debug=debug

    def start_debug(self, mode: bool):
        self.debug = mode

    # Appending the message to long-term memory
    def append_long_term_memory(self, message: Dict[str, Any]):
        self.long_memory.append(message)
        if len(self.short_memory) > self.max_short_term:
            self.long_memory.pop(0)
    
    # Appending the message to short-term memory
    def append_short_term_memory(self, message: Dict[str, Any]):
        self.short_memory.append(message)
        if len(self.long_memory) > self.max_short_term:
            self.short_memory.pop(0)

    # Retrieving context from the recent conversation and key information about the conversation 
    def get_context(self):
        context = "Previous Conversation:\n"
        context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in self.short_memory[-5:]])
        
        if self.long_memory:
            context = "\n\nKey Info:\n"
            context = "\n".join([f"- {msg['content']}" for msg in self.long_memory[-3:]])

        return context            
    
    def importance_evaluator(self, client: Agent, data: Dict[str, Any]):
        prompt = f"""Rate the importance of remembering this information based on the overall conversation on a scale of 1-10:
        Text: "{data}"
        Respond only with a number."""
        
        if self.debug:
            print("=============INPUT INFO=============")
            print(f"received data:\t{data}\n")
            print(f"added prompt:\t{prompt}\n")
        
        response = client.invoke(prompt)
        
        if self.debug:
            print("=============OUTPUT INFO=============")
            print(f"response prompt{response}\n")
        return int(response) >=7

    def update_memory(self, client:Agent, human_input: str, ai_output: str):
        human_frame = {"role": "user", "content": human_input} 
        ai_frame = {"role": "system", "content": ai_output}
        
        if self.debug:
            print("=============INPUT INFO=============")
            print(f"received human input:\t{human_input}")
            print(f"received AI input:\t{ai_output}\n")
            print("=============MEMORY INFO=============")
            print(f"pre-append length of short memory:\t{len(self.short_memory)}")
            print(f"pre-append length of long memory:\t{len(self.long_memory)}")
            self.append_short_term_memory(human_frame)
            self.append_short_term_memory(ai_frame)
            print(f"new length of short memory:\t{len(self.short_memory)}")
            print(f"new length of long memory:\t{len(self.long_memory)}\n")

        self.append_short_term_memory(human_frame)
        self.append_short_term_memory(ai_frame)
        
        # Example heuristics for long-term memory (manual, delegated)
        if "remember this" or "record this" in human_input.lower():
            self.append_long_term_memory(human_frame)
            self.append_long_term_memory(ai_frame)
        elif self.importance_evaluator(client, human_input) == True:
            self.append_long_term_memory(human_frame)
            self.append_long_term_memory(ai_frame)