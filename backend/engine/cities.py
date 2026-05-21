"""Registry of cities supported by the CityFlow router.

Adding a new city only requires appending an entry here — the rest of the
backend (startup warmup, snap-point, route endpoint) reads from this
dictionary.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class CityConfig:
    slug: str          # stable machine identifier, used in API payloads
    display_name: str  # human-friendly label, shown in the UI
    center: tuple      # (lat, lon)
    radius_meters: int

    @property
    def coverage_radius(self) -> int:
        return self.radius_meters


CITIES = {
    "vila_real": CityConfig(
        slug="vila_real",
        display_name="Vila Real",
        center=(41.296, -7.746),
        radius_meters=1500,
    ),
    "paris": CityConfig(
        slug="paris",
        display_name="Paris",
        center=(48.8584, 2.347),
        radius_meters=1500,
    ),
}

DEFAULT_CITY = "vila_real"


def get_city(slug: str) -> CityConfig:
    return CITIES.get(slug, CITIES[DEFAULT_CITY])


def list_cities() -> list[dict]:
    """Public-facing list used by the /cities endpoint."""
    return [
        {
            "slug": c.slug,
            "display_name": c.display_name,
            "center": list(c.center),
            "radius_meters": c.radius_meters,
        }
        for c in CITIES.values()
    ]
