"""Registo das cidades suportadas pelo router do CityFlow.

Adicionar uma nova cidade requer apenas uma entrada neste dicionário —
o resto do backend (warmup de arranque, snap-point, endpoint de rotas)
lê deste registo.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class CityConfig:
    slug: str          # identificador estável usado nos payloads da API
    display_name: str  # rótulo apresentado na interface
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
    """Lista pública usada pelo endpoint /cities."""
    return [
        {
            "slug": c.slug,
            "display_name": c.display_name,
            "center": list(c.center),
            "radius_meters": c.radius_meters,
        }
        for c in CITIES.values()
    ]
