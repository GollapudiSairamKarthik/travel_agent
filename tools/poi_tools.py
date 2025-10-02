from tools.geocode import geocode_city
from tools.poi_fetcher import fetch_pois

def poi_tool(city: str, radius: int = 2000, limit: int = 8) -> str:
    """Return POIs near a city. Args: city (str), radius (int meters), limit (int)."""
    g = geocode_city(city)
    if g is None:
        return f"ERROR: Could not geocode '{city}'."
    
    pois = fetch_pois(g["lat"], g["lon"], radius=radius, limit=limit)
    if not pois:
        return f"WARNING: No POIs found for {g['name']}."
    
    lines = [f"Top {len(pois)} POIs near {g['name']}:"] + [
        f"{i+1}. {p['name']} ({p.get('tags', {})})" for i, p in enumerate(pois)
    ]
    return "\n".join(lines)
