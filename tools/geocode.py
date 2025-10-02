import requests
from typing import Optional, Dict, Any

def geocode_city(city: str) -> Optional[Dict[str, Any]]:
    """Simple geocoding using Nominatim (OpenStreetMap)."""
    try:
        url = "https://nominatim.openstreetmap.org/search"
        r = requests.get(
            url,
            params={"q": city, "format": "json", "limit": 1},
            headers={"User-Agent": "travel-agent-app"},
            timeout=10,
        )
        r.raise_for_status()
        results = r.json()
        if not results:
            return None
        res = results[0]
        return {
            "lat": float(res["lat"]),
            "lon": float(res["lon"]),
            "name": res.get("display_name", city),
        }
    except Exception:
        return None
