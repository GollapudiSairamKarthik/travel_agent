# agents/poi_agent.py
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from tools.poi_tools import poi_tool as poi_tool_func

def build_poi_agent(model: str, api_key: str, base_url: str, temperature: float = 0.2):
    """
    Build a standalone POI agent.
    Exposes `poi_tool(city, radius, limit)`.
    """
    llm = ChatOpenAI(model=model, api_key=api_key, base_url=base_url, temperature=temperature)
    agent = create_react_agent(
        model=llm,
        tools=[poi_tool_func],
        prompt=(
            "You are a points-of-interest assistant. When asked, return a readable list "
            "of top POIs for a city, with short descriptions. Use the poi_tool."
        ),
    )
    return agent
