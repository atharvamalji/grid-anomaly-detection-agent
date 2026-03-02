"""Representative lat/lon per balancing authority, for weather lookups.

Balancing authorities span large, irregular multi-state footprints — a single
point cannot represent conditions across the whole territory. These are
population-weighted-ish central/major cities within each BA's footprint,
chosen as a reasonable single representative point for a demo enrichment
feature, not a claim of full-territory accuracy.
"""

REGION_COORDINATES: dict[str, tuple[float, float]] = {
    # Indianapolis, IN — central to MISO's footprint
    "MISO": (39.7684, -86.1581),
    # Columbus, OH — central to PJM's footprint
    "PJM": (39.9612, -82.9988),
    # Wichita, KS — central to SPP's footprint (EIA-930 code SWPP)
    "SWPP": (37.6872, -97.3301),
}


def get_coordinates(region: str) -> tuple[float, float] | None:
    return REGION_COORDINATES.get(region.upper())
