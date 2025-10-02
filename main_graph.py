# main_graph.py
from __future__ import annotations
import os
import sys
from dotenv import load_dotenv
from typing import List, Callable

# LangGraph / LangChain wrapper
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI

# load .env if present
load_dotenv()

# Config from env (.env recommended)
GROQ_API_KEY = os.getenv("GROQ_API_KEY") or os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "https://api.groq.com/openai/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")


def _preflight_check():
    """
    Ensure an API key is present and not a placeholder.
    If missing or placeholder-like, print a clear message and exit.
    """
    if not GROQ_API_KEY:
        msg = (
            "ERROR: No API key found. Please set GROQ_API_KEY (or OPENAI_API_KEY) in your environment or .env file.\n"
            "Example in .env:\n"
            "  GROQ_API_KEY=gsk_your_real_key_here\n"
            "  OPENAI_API_BASE=https://api.groq.com/openai/v1\n"
        )
        print(msg, file=sys.stderr)
        # Do not sys.exit here when imported by tests — but raise so the app fails early.
        raise RuntimeError("No GROQ_API_KEY / OPENAI_API_KEY set. See stderr message.")
    # quick sanity check for placeholder values:
    if "YOUR" in GROQ_API_KEY.upper() or GROQ_API_KEY.strip().endswith("_HERE"):
        raise RuntimeError("GROQ_API_KEY looks like a placeholder. Replace it with a real key.")


def get_supervisor():
    """
    Build and return a LangGraph REACT-style supervisor agent.
    The Streamlit app expects this function to exist and return an agent object.
    """
    # Preflight: ensure API key present
    _preflight_check()

    # Import the tools shim (tools.py). This module re-exports the three callables.
    try:
        import tools  # the top-level shim that exposes weather_tool, poi_tool, itinerary_tool
    except Exception as e:
        raise ImportError(
            "Failed to import top-level 'tools' shim module. Ensure tools.py exists at project root and "
            "exposes callables weather_tool, poi_tool, itinerary_tool. Original error: %s" % str(e)
        ) from e

    # Validate exported functions
    for name in ("weather_tool", "poi_tool", "itinerary_tool"):
        if not hasattr(tools, name) or not callable(getattr(tools, name)):
            raise ImportError(f"tools module does not export callable {name}. Please expose it in tools.py or tools/* modules.")

    # Collect the actual callables
    weather_tool = getattr(tools, "weather_tool")
    poi_tool = getattr(tools, "poi_tool")
    itinerary_tool = getattr(tools, "itinerary_tool")

    # Build LLM wrapper — this will raise a clear exception if the key is invalid
    llm = ChatOpenAI(
        model=LLM_MODEL,
        api_key=GROQ_API_KEY,
        base_url=OPENAI_API_BASE,
        temperature=0.2,
    )

    # Create the REACT-style supervisor agent using the three tools
    agent = create_react_agent(
        model=llm,
        tools=[weather_tool, poi_tool, itinerary_tool],
        prompt=(
            "You are a travel-planning supervisor. Tools available:\n"
            "- weather_tool(city, start_date, end_date) -> returns weather summary\n"
            "- poi_tool(city, radius, limit) -> returns POIs list\n"
            "- itinerary_tool(city, start_date, end_date, daily_limit) -> returns itinerary\n\n"
            "When calling tools, send city names and dates as strings and numeric values as integers.\n"
            "Produce a final reply containing weather, POIs, and a day-by-day itinerary table with a Notes column."
        ),
    )
    return agent


# Allow running this module directly for a sanity check
if __name__ == "__main__":
    try:
        a = get_supervisor()
        print("Supervisor built:", type(a))
    except Exception as e:
        print("Failed to build supervisor:", repr(e))
        raise
