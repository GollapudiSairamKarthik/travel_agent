# agents/weather_agent.py
from typing import Optional, Dict, Any
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI

from tools.weather_tools import weather_tool as weather_tool_func
from tools.geocode import geocode_city

def build_weather_agent(model: str, api_key: str, base_url: str, temperature: float = 0.2):
    """
    Build a standalone weather agent.
    Exposes a single tool `weather_tool(city, start_date, end_date)`.
    """
    llm = ChatOpenAI(model=model, api_key=api_key, base_url=base_url, temperature=temperature)
    agent = create_react_agent(
        model=llm,
        tools=[weather_tool_func],
        prompt=(
            "You are a focused weather assistant. When asked, return a concise daily "
            "weather summary for the given city and date range. Use the weather_tool."
        ),
    )
    return agent
