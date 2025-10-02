import requests
from typing import List, Dict, Any

def fetch_pois(lat: float, lon: float, radius: int = 2000, limit: int = 8) -> List[Dict[str, Any]]:
    """Fetch POIs using Overpass API (fallback if OpenTripMap not used)."""
    try:
        query = f"""
        [out:json][timeout:15];
        (
          node(around:{radius},{lat},{lon})["tourism"];
          way(around:{radius},{lat},{lon})["tourism"];
          node(around:{radius},{lat},{lon})["historic"];
          way(around:{radius},{lat},{lon})["historic"];
          node(around:{radius},{lat},{lon})["leisure"];
          way(around:{radius},{lat},{lon})["leisure"];
          node(around:{radius},{lat},{lon})["amenity"~"museum|theatre|gallery|marketplace|park"];
        );
        out center {limit};
        """
        r = requests.post("https://overpass-api.de/api/interpreter", data=query.encode("utf-8"), timeout=20)
        r.raise_for_status()
        el = r.json().get("elements", [])
        results = []
        seen = set()
        for e in el:
            tags = e.get("tags", {})
            name = tags.get("name")
            if not name:
                continue
            key = name.strip().lower()
            if key in seen:
                continue
            seen.add(key)
            results.append({"name": name, "tags": tags})
            if len(results) >= limit:
                break
        return results
    except Exception:
        return []
