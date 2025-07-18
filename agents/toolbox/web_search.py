from langchain_tavily import TavilySearch
from langchain_core.tools import Tool

# general search tool to retrieve basic search results
search_tool = Tool(TavilySearch(
    max_results=5,
    topic="general"
)
)
# news search tool to retrieve current events
news_search_tool = Tool(TavilySearch(
    max_results=5,
    topic="news",
    time_range="day"
))

# finance search tool to retrieve recent financial data
finance_search_tool = Tool(TavilySearch(
    max_results=5,
    topic="finance",
    time_range="day"
))

