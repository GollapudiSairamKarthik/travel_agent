from dateutil.parser import parse as parse_date
import datetime
from tools.geocode import geocode_city
from tools.weather_fetcher import fetch_weather

def weather_tool(city: str, start_date: str = None, end_date: str = None) -> str:
    """Return weather summary for a city and date range."""
    g = geocode_city(city)
    if g is None:
        return f"ERROR: Could not geocode '{city}'."
    
    lat, lon = g["lat"], g["lon"]
    name = g["name"]

    if not start_date:
        start_date = datetime.date.today().isoformat()
    if not end_date:
        end_date = start_date

    try:
        sd = parse_date(start_date).date().isoformat()
        ed = parse_date(end_date).date().isoformat()
    except Exception:
        return "ERROR: Dates must be YYYY-MM-DD."

    weather = fetch_weather(lat, lon, sd, ed)
    if not weather:
        return f"WARNING: No weather data for {name} between {sd} and {ed}."

    lines = [f"Weather for {name} ({sd} to {ed}):"]
    times = weather.get("time", [])
    tmax = weather.get("temperature_2m_max", [])
    tmin = weather.get("temperature_2m_min", [])
    prec = weather.get("precipitation_sum", [])
    for i, d in enumerate(times):
        mx = tmax[i] if i < len(tmax) else "N/A"
        mn = tmin[i] if i < len(tmin) else "N/A"
        pr = prec[i] if i < len(prec) else "N/A"
        lines.append(f"- {d}: max {mx}°C, min {mn}°C, precipitation {pr} mm")

    return "\n".join(lines)
