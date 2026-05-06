import inspect
from nltk.tokenize import sent_tokenize, word_tokenize
from agent import Agent
from typing import List, Dict, Any, Optional, TypedDict 

"""
    Memory Module Development Progress:
        As of 9/3/25:
            - The method of appending memory is complete.
            - The conditions for adding have now been fixed, no empty inputs are added.
            - Next, the heuristics will need to be improved to improve the quality of 
                context used to better track the nature of the conversation of the user and the assistant.
            - In addition, the deletion of unecessary long term memories will be part of 
                the tracking method for the conversation.
            - [9/9/25] Problems within the access of the agent module continue to persist...
                * Possibly through the way the package is being accessed. 
                    More research on package creation is needed to solve this issue.
"""

class Memory:
    def __init__(self, max_short_term=10, max_long_term=50, debug=False):
        self.short_memory = []
        self.long_memory = []
        self.max_short_term = max_short_term
        self.max_long_term = max_long_term
        self.debug=debug

    def start_debug(self, mode: bool):
        print("Changing Memory to debug mode...")
        self.debug = mode
        print(f"debug: {self.debug}")
        return

    def append_long_term_memory(self, message: Dict[str, Any]): # Updating the long-term memory with the new message
        self.long_memory.append(message)
        self.pop_memory_list(self.long_memory, self.max_long_term)
    
    def append_short_term_memory(self, message: Dict[str, Any]): # Updating the short-term memory with the new message
        self.short_memory.append(message)
        self.pop_memory_list(self.short_memory, self.max_short_term)

    def pop_memory_list(self, memory: list, limit: int):
        if len(memory) > limit:
            memory.pop(0)

    # Retrieving context from the recent conversation and key information about the conversation 
    def get_context(self):
        context = "Previous Conversation:\n"
        context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in self.short_memory[-5:]])
        if self.debug:
            function_name = inspect.currentframe().f_code.co_name.upper()
            print(f"\n============={function_name}=============")
            print(f"short term memory context:\t{context}\n")
        
        if self.long_memory:
            context = "\n\nKey Info:\n"
            context = "\n".join([f"- {msg['content']}" for msg in self.long_memory[-3:]])
            if self.debug:
                print(f"short & long term memory context:\t{context}\n")

        return context            
    
    def importance_evaluator(self, client: Agent, data: Dict[str, Any]):
        prompt = f"""Rate the importance of remembering this information based on the overall conversation on a scale of 1-10:
        Text: "{data}"
        Respond only with a number."""
        
        if self.debug:
            function_name = inspect.currentframe().f_code.co_name.upper()
            print(f"\n============={function_name}_INPUT=============")
            print(f"received data:\t{data}\n")
            print(f"added prompt:\t{prompt}\n")
        
        response = client.invoke(prompt)
        
        if self.debug:
            print(f"\n============={function_name}_OUTPUT=============")
            print(f"response prompt{response}\n")
        return int(response) >=7

    def update_memory(self, client:Agent, human_input: str = None, ai_output: str = None):
        human_frame = {"role": "user", "content": human_input} 
        ai_frame = {"role": "system", "content": ai_output}
        
        if self.debug:
            function_name = inspect.currentframe().f_code.co_name.upper()
            print(f"\n============={function_name}_INPUT=============")
            print(f"received human input:\t{human_input}")
            print(f"received AI input:\t{ai_output}\n")
            print("\n=============MEMORY_INFO=============")
            print(f"pre-append length of short memory:\t{len(self.short_memory)}")
            print(f"pre-append length of long memory:\t{len(self.long_memory)}")

        if human_frame["content"] != None:
            self.append_short_term_memory(human_frame)
        if ai_frame["content"] != None:
            self.append_short_term_memory(ai_frame)

        if self.debug:
            print(f"new length of short memory:\t{len(self.short_memory)}")
            print(f"new length of long memory:\t{len(self.long_memory)}\n")

        # Example heuristics for long-term memory (manual, delegated)
        if "remember this" or "record this" in human_input.lower():
            self.append_long_term_memory(human_frame)
            if ai_frame["content"] != None:
                self.append_long_term_memory(ai_frame)
        elif self.importance_evaluator(client, human_input) == True:
            self.append_long_term_memory(human_frame)
            if ai_frame["content"] != None:
                self.append_long_term_memory(ai_frame)

if __name__ == "__main__":
    """
        currently working on implementing intent classification and topic classification based on the series of 
            messages to determine the appropriate subject of the conversation.
    """
    example_string_list = ["""Can you help me solve this 2+3/4*6?""", """what is the circumference of a circle with a radius of 83.0302 in?""","""what are the first 5 numbers in eulers number?""","""what is another way of representing log 64 base 8?"""]
    for i in example_string_list:
        print(i)
