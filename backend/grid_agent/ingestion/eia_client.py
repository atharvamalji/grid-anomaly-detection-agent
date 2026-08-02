import os

import requests

EIA_BASE_URL = "https://api.eia.gov/v2"
REGION_DATA_ROUTE = "electricity/rto/region-data/data"


class EIAClient:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.environ.get("EIA_API_KEY")
        if not self.api_key:
            raise ValueError(
                "EIA API key required — set EIA_API_KEY or pass api_key explicitly. "
                "Get a free key at https://www.eia.gov/opendata/"
            )

    def fetch_hourly_demand(
        self,
        respondent: str,
        start: str,
        end: str,
    ) -> list[dict]:
        """Fetch hourly demand (type=D) for a balancing authority (e.g. "MISO").

        start/end are ISO date-hour strings, e.g. "2026-01-01T00" (UTC, per EIA-930).
        Returns raw records from the API's "data" list.
        """
        params = {
            "api_key": self.api_key,
            "frequency": "hourly",
            "data[0]": "value",
            "facets[respondent][]": respondent,
            "facets[type][]": "D",
            "start": start,
            "end": end,
            "sort[0][column]": "period",
            "sort[0][direction]": "asc",
            "offset": 0,
            "length": 5000,
        }

        records: list[dict] = []
        while True:
            try:
                resp = requests.get(
                    f"{EIA_BASE_URL}/{REGION_DATA_ROUTE}", params=params, timeout=30
                )
                resp.raise_for_status()
            except requests.RequestException as e:
                raise RuntimeError(f"EIA API request failed: {e}") from e

            payload = resp.json().get("response", {})
            batch = payload.get("data", [])
            records.extend(batch)

            if len(batch) < params["length"]:
                break
            params["offset"] += params["length"]

        return records
