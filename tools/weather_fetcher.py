import requests

def fetch_weather(lat: float, lon: float, start_date: str, end_date: str) -> dict:
    """Fetch daily weather block from Open-Meteo API for given date range."""
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode",
            "start_date": start_date,
            "end_date": end_date,
            "timezone": "auto",
        }
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        return r.json().get("daily", {})
    except Exception:
        return {}
