# tools.py
"""
Top-level tools shim.

This file re-exports the three callables the supervisor expects:
- weather_tool(city, start_date, end_date)
- poi_tool(city, radius, limit)
- itinerary_tool(city, start_date, end_date, daily_limit)

It tries to import the real implementations from the `tools` package
(e.g. tools/weather_tools.py, tools/poi_tools.py, tools/itinerary_tools.py).
If those modules are not present or the functions are missing, it raises
a clear ImportError with guidance.
"""
from __future__ import annotations
import importlib
import os
from typing import Callable

CANDIDATE_MODULES = [
    "tools.weather_tools",    # recommended
    "tools.poi_tools",
    "tools.itinerary_tools",
    # fallback names that some projects use:
    "tools.weather_tools",
    "tools.poi_tools",
    "tools.itinerary_tools",
]

_missing_msg = (
    "Could not locate required tool functions: ['weather_tool','poi_tool','itinerary_tool'].\n"
    "Make sure your project exposes these callables (module-level) in one of:\n"
    "  - tools/weather_tools.py (weather_tool)\n"
    "  - tools/poi_tools.py (poi_tool)\n"
    "  - tools/itinerary_tools.py (itinerary_tool)\n"
    "Or expose them at top-level travel_agent.py as legacy fallback."
)


def _try_import(name: str):
    try:
        return importlib.import_module(name)
    except Exception:
        return None


# Try to import explicit modules that contain each tool.
_weather = None
_poi = None
_itin = None

# First try the explicit recommended modules
mod_weather = _try_import("tools.weather_tools")
mod_poi = _try_import("tools.poi_tools")
mod_itin = _try_import("tools.itinerary_tools")

if mod_weather and hasattr(mod_weather, "weather_tool"):
    _weather = getattr(mod_weather, "weather_tool")
if mod_poi and hasattr(mod_poi, "poi_tool"):
    _poi = getattr(mod_poi, "poi_tool")
if mod_itin and hasattr(mod_itin, "itinerary_tool"):
    _itin = getattr(mod_itin, "itinerary_tool")

# Fallback: maybe the project used single-file travel_agent.py (legacy)
if not (_weather and _poi and _itin):
    try:
        import travel_agent as ta  # type: ignore
    except Exception:
        ta = None
    else:
        if not _weather and hasattr(ta, "weather_tool"):
            _weather = getattr(ta, "weather_tool")
        if not _poi and hasattr(ta, "poi_tool"):
            _poi = getattr(ta, "poi_tool")
        if not _itin and hasattr(ta, "itinerary_tool"):
            _itin = getattr(ta, "itinerary_tool")

# Final validation
if not (_weather and _poi and _itin):
    missing = []
    if not _weather:
        missing.append("weather_tool")
    if not _poi:
        missing.append("poi_tool")
    if not _itin:
        missing.append("itinerary_tool")
    raise ImportError(
        f"Could not locate required tool functions: {missing}. Ensure your project exposes {', '.join(missing)}.\n"
        "Expected module locations: tools/weather_tools.py, tools/poi_tools.py, tools/itinerary_tools.py, or travel_agent.py"
    )

# Export the found callables at module-level (so `import tools; tools.weather_tool` works)
weather_tool: Callable = _weather
poi_tool: Callable = _poi
itinerary_tool: Callable = _itin


# Optional: small runtime preflight helper (not executed on import)
def preflight_print():
    """Print a short masked diagnostics (safe to call in web UI)"""
    key = os.getenv("GROQ_API_KEY") or os.getenv("OPENAI_API_KEY") or ""
    masked = None
    if key:
        masked = key[:6] + "..." + key[-4:] if len(key) > 12 else key[:3] + "..."
    print("tools shim: weather_tool=%s, poi_tool=%s, itinerary_tool=%s, GROQ_key=%s"
          % (callable(weather_tool), callable(poi_tool), callable(itinerary_tool), masked))
