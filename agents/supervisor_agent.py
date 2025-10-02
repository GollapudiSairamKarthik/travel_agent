# agents/supervisor_agent.py
from typing import Callable
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI

from agents.weather_agent import build_weather_agent
from agents.poi_agent import build_poi_agent
from agents.itinerary_agent import build_itinerary_agent

# We will return the supervisor agent that has wrapper tools that call the child agents.
# These wrappers must have docstrings (for schema conversion).

def build_supervisor_agent(model: str, api_key: str, base_url: str, temperature: float = 0.2):
    # Build child agents
    weather_agent = build_weather_agent(model, api_key, base_url, temperature)
    poi_agent = build_poi_agent(model, api_key, base_url, temperature)
    itinerary_agent = build_itinerary_agent(model, api_key, base_url, temperature)

    # wrapper functions that call the child agents' invoke and return their output
    def weather_agent_call(city: str, start_date: str, end_date: str) -> str:
        """Call the weather agent. Args: city (str), start_date (YYYY-MM-DD), end_date (YYYY-MM-DD)."""
        payload = {"messages": [{"role": "user", "content": f"Provide weather for {city} from {start_date} to {end_date}."}]}
        state = weather_agent.invoke(payload)
        # extract best textual output robustly:
        msgs = state.get("messages", []) if isinstance(state, dict) else []
        for m in msgs:
            if isinstance(m, dict) and m.get("content"):
                return m.get("content")
        # fallback
        return str(state)

    def poi_agent_call(city: str, radius: int = 2000, limit: int = 8) -> str:
        """Call the POI agent. Args: city (str), radius (int), limit (int)."""
        payload = {"messages": [{"role": "user", "content": f"Find POIs near {city}; radius={radius}; limit={limit}."}]}
        state = poi_agent.invoke(payload)
        msgs = state.get("messages", []) if isinstance(state, dict) else []
        for m in msgs:
            if isinstance(m, dict) and m.get("content"):
                return m.get("content")
        return str(state)

    def itinerary_agent_call(city: str, start_date: str, end_date: str, daily_limit: int = 3) -> str:
        """Call the itinerary agent. Args: city (str), start_date (YYYY-MM-DD), end_date (YYYY-MM-DD), daily_limit (int)."""
        payload = {"messages": [{"role": "user", "content": f"Create itinerary for {city} from {start_date} to {end_date}, daily_limit={daily_limit}."}]}
        state = itinerary_agent.invoke(payload)
        msgs = state.get("messages", []) if isinstance(state, dict) else []
        for m in msgs:
            if isinstance(m, dict) and m.get("content"):
                return m.get("content")
        return str(state)

    # now create supervisor LLM
    llm = ChatOpenAI(model=model, api_key=api_key, base_url=base_url, temperature=temperature)

    # register wrappers as tools for the supervisor: they must have docstrings (they do)
    agent = create_react_agent(
        model=llm,
        tools=[weather_agent_call, poi_agent_call, itinerary_agent_call],
        prompt=(
            "You are a travel supervisor. Coordinate the weather agent, the POI agent "
            "and the itinerary agent. Decide which agent to call and when, fetch results "
            "and synthesize a final plan that includes weather, POIs and an itinerary table."
        ),
    )
    return agent
