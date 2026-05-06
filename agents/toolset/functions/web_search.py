from langchain_tavily import TavilySearch
from langchain_tavily.tavily_extract import TavilyExtract
from langchain_core.tools import Tool

# general search tool to retrieve basic search results
# search_tool = Tool(
#     name="search_tool",
#     func=TavilySearch(max_results=5, topic="general"),
#     description="General search tool",
# )
# # news search tool to retrieve current events
# news_search_tool = Tool(
#     name="news_search_tool",
#     func=TavilySearch(max_results=5, topic="news", time_range="day"),
#     description="News search tool",
# )

# # finance search tool to retrieve recent financial data
# finance_search_tool = Tool(
#     name="finance_search_tool",
#     func=TavilySearch(max_results=5, topic="finance", time_range="day"),
#     description="Financial search tool",
# )


def testing():
    output = TavilySearch(max_results=5, topic="finance", time_range="day").invoke(
        {"query": "what is the current valuation of NASDAQ"}
    )
    print(output)


def web_search(topic, max_results, time_range, query):
    # In progress, this function will conduct the search and extraction of the most relevant results to the agent.
    construct = TavilySearch(
        max_results=max_results, time_range=time_range, topic=topic
    )
    search_results = construct.invoke({"query": query})
    results = []
    for i in search_results:
        results.append(TavilyExtract.invoke({"input": i}))
    print(results)
    return results


# if __name__ == "__main__":
#     query = "What are the current fortune 500?"
#     web_search( topic="finance", max_results=5, time_range="month", query=query )
