import inspect
from langchain_core.tools import Tool
from functions import calculator
from functions import doc_reader
from functions import web_search

# This module is here to consolidate and house all types of supported tools in the agent's architecture. Any tool addition will automatically included in the list of supported functionalities.
# This module could also make langchain's vector store handling easier.

Calculator = Tool( name="calculator",
    func= calculator.calculator,
    description="A math tool specifically used for PEMDAS calculations.")

Doc_Reader = Tool(name="doc_reader",
    func=doc_reader.doc_reader,
    description="Useful document reader function for pdf text extraction purposes.")

# General search tool to retrieve basic search results
Web_Search = Tool(
    name="search_tool",
    func=web_search.web_search,
    description="A Web search tool that allows for targeted queries based on topic categories and time ranges."
)

def function_name_getter():
    func_name_list = []
    items = inspect.currentframe().f_globals.items()
    for key, value in items:
        if isinstance(value, Tool):
          func_name_list.append([value.name, value.description])
        #   func_name_list.append(value)
    return func_name_list