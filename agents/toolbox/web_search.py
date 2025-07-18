from langchain_tavily import TavilySearch
from langchain_core.tools import Tool

# general search tool to retrieve basic search results
search_tool = Tool(
    name="search_tool",
    func=TavilySearch(
    max_results=5,
    topic="general"
),
description="General search tool"
)
# news search tool to retrieve current events
news_search_tool = Tool(
    name="news_search_tool",
    func=TavilySearch(
    max_results=5,
    topic="news",
    time_range="day"
),
description="News search tool"
)

# finance search tool to retrieve recent financial data
finance_search_tool = Tool(
    name="finance_search_tool",
    func=TavilySearch(
    max_results=5,
    topic="finance",
    time_range="day"
),
description="Financial search tool"
)

