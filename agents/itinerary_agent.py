# agents/itinerary_agent.py
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from tools.itinerary_tools import itinerary_tool as itinerary_tool_func

def build_itinerary_agent(model: str, api_key: str, base_url: str, temperature: float = 0.2):
    """
    Build a standalone itinerary agent.
    Exposes `itinerary_tool(city, start_date, end_date, daily_limit)`.
    """
    llm = ChatOpenAI(model=model, api_key=api_key, base_url=base_url, temperature=temperature)
    agent = create_react_agent(
        model=llm,
        tools=[itinerary_tool_func],
        prompt=(
            "You are an itinerary planner. Given city, dates and POIs/weather info, "
            "produce a day-by-day itinerary (Morning/Afternoon/Evening) and a Notes column."
        ),
    )
    return agent
