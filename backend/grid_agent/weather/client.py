from dataclasses import dataclass
from datetime import datetime

import requests

ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"


@dataclass
class WeatherObservation:
    timestamp: str
    latitude: float
    longitude: float
    temperature_c: float | None
    apparent_temperature_c: float | None
    wind_speed_kmh: float | None

    def summary(self) -> str:
        parts = []
        if self.temperature_c is not None:
            parts.append(f"{self.temperature_c:.1f}°C")
        if self.apparent_temperature_c is not None:
            parts.append(f"feels like {self.apparent_temperature_c:.1f}°C")
        if self.wind_speed_kmh is not None:
            parts.append(f"wind {self.wind_speed_kmh:.0f} km/h")
        return ", ".join(parts) if parts else "no data"


class OpenMeteoClient:
    """Free, no-API-key historical weather via Open-Meteo's archive API."""

    def __init__(self, base_url: str = ARCHIVE_URL, timeout: int = 15):
        self.base_url = base_url
        self.timeout = timeout

    def get_historical_hourly(
        self, latitude: float, longitude: float, timestamp: str
    ) -> WeatherObservation | None:
        """Fetch the weather observation nearest to `timestamp` (any parseable
        ISO-ish string, e.g. "2025-12-14 16:00:00+00:00") at the given point.
        Returns None if the lookup fails rather than raising, since weather
        enrichment should degrade gracefully — the agent can still explain
        anomalies from RAG context alone if this is unavailable.
        """
        try:
            dt = datetime.fromisoformat(timestamp)
        except ValueError:
            return None

        date_str = dt.date().isoformat()
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": date_str,
            "end_date": date_str,
            "hourly": "temperature_2m,apparent_temperature,wind_speed_10m",
            "timezone": "UTC",
        }

        try:
            resp = requests.get(self.base_url, params=params, timeout=self.timeout)
            resp.raise_for_status()
        except requests.RequestException:
            return None

        payload = resp.json().get("hourly", {})
        times = payload.get("time", [])
        if not times:
            return None

        target_hour = dt.strftime("%Y-%m-%dT%H:00")
        try:
            idx = times.index(target_hour)
        except ValueError:
            return None

        def _at(key: str) -> float | None:
            values = payload.get(key, [])
            return values[idx] if idx < len(values) else None

        return WeatherObservation(
            timestamp=target_hour,
            latitude=latitude,
            longitude=longitude,
            temperature_c=_at("temperature_2m"),
            apparent_temperature_c=_at("apparent_temperature"),
            wind_speed_kmh=_at("wind_speed_10m"),
        )
