import datetime
from dateutil.parser import parse as parse_date
from tools.geocode import geocode_city
from tools.poi_fetcher import fetch_pois
from tools.weather_fetcher import fetch_weather

def itinerary_tool(city: str, start_date: str, end_date: str, daily_limit: int = 3) -> str:
    """Return a markdown itinerary.
    Args:
        city (str): City name
        start_date (YYYY-MM-DD)
        end_date (YYYY-MM-DD)
        daily_limit (int): POIs per day
    """
    g = geocode_city(city)
    if g is None:
        return f"ERROR: Could not geocode '{city}'."

    try:
        sd = parse_date(start_date).date()
        ed = parse_date(end_date).date()
    except Exception:
        return "ERROR: Dates must be YYYY-MM-DD."

    if ed < sd:
        return "ERROR: end_date must be same or after start_date."

    num_days = (ed - sd).days + 1
    pool_pois = fetch_pois(g["lat"], g["lon"], radius=3500, limit=max(20, daily_limit * num_days * 2))
    poi_lines = "\n".join([f"- {p['name']} ({p.get('kinds','')})" for p in pool_pois]) if pool_pois else "No POIs found."

    weather = fetch_weather(g["lat"], g["lon"], sd.isoformat(), ed.isoformat())
    precip = weather.get("precipitation_sum", [])
    tmax = weather.get("temperature_2m_max", [])
    tmin = weather.get("temperature_2m_min", [])

    indoor_kinds = {"museum", "theatre", "gallery", "library", "cinema"}
    pool = []
    for p in pool_pois:
        kinds = (p.get("kinds") or "").lower()
        is_indoor = any(k in kinds for k in indoor_kinds)
        pool.append({"name": p.get("name"), "is_indoor": is_indoor, "kinds": kinds})

    assigned = set()
    rows = []
    idx = 0

    def weather_note_for_day(i: int) -> str:
        note_parts = []
        if i < len(precip):
            try:
                pr = float(precip[i])
            except Exception:
                pr = 0.0
            if pr >= 10.0:
                note_parts.append("Heavy rain expected — favor indoor activities")
            elif pr >= 2.0:
                note_parts.append("Chance of rain — have indoor alternatives")
            elif pr > 0:
                note_parts.append("Light showers possible")
            else:
                note_parts.append("Good weather for walking")
        if i < len(tmax) and i < len(tmin):
            try:
                mx = float(tmax[i]); mn = float(tmin[i])
                if mx >= 30:
                    note_parts.append("Hot during day")
                elif mx <= 15:
                    note_parts.append("Cool day — bring a jacket")
            except Exception:
                pass
        return "; ".join(note_parts) if note_parts else "No specific weather notes"

    for day_index in range(num_days):
        date = (sd + datetime.timedelta(days=day_index)).isoformat()
        rainy = False
        if day_index < len(precip):
            try:
                rainy = float(precip[day_index]) >= 2.0
            except Exception:
                rainy = False

        day_selected = []
        attempts = 0
        while len(day_selected) < daily_limit and attempts < max(1, len(pool)) * 2:
            p = pool[idx % max(1, len(pool))] if pool else None
            idx += 1; attempts += 1
            if p is None:
                break
            if p["name"] in assigned:
                continue
            if rainy and not p["is_indoor"]:
                continue
            day_selected.append(p["name"])
            assigned.add(p["name"])
        if len(day_selected) < daily_limit:
            for p in pool:
                if p["name"] in assigned:
                    continue
                day_selected.append(p["name"])
                assigned.add(p["name"])
                if len(day_selected) >= daily_limit:
                    break

        morning = day_selected[0] if len(day_selected) > 0 else "Free / explore locally"
        afternoon = day_selected[1] if len(day_selected) > 1 else "Free / explore locally"
        evening = day_selected[2] if len(day_selected) > 2 else "Dinner / relax"
        notes = weather_note_for_day(day_index)
        rows.append({"date": date, "morning": morning, "afternoon": afternoon, "evening": evening, "notes": notes})

    md = []
    md.append(f"# Itinerary for {g.get('name')}")
    md.append(f"Dates: {sd.isoformat()} to {ed.isoformat()}")
    md.append("")
    md.append("## Travel Itinerary")
    md.append("")
    md.append("| Day | Morning | Afternoon | Evening | Notes |")
    md.append("|---:|---|---|---|---|")
    for i, r in enumerate(rows, start=1):
        md.append(f"| {i} | {r['morning']} | {r['afternoon']} | {r['evening']} | {r['notes']} |")
    md.append("")
    md.append("## POIs considered")
    md.append(poi_lines)
    return "\n".join(md)
