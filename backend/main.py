import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from engine.cities import CITIES, DEFAULT_CITY, get_city, list_cities
from engine.router import CityFlowRouter
from models import RouteRequest, SnapPointRequest

logging.basicConfig(level=logging.INFO, format="%(levelname)s\t%(name)s: %(message)s")
log = logging.getLogger(__name__)

app = FastAPI(title="CityFlow Inclusive API", version="1.3")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# One router instance per supported city; both graphs are warmed at startup.
routers: dict[str, CityFlowRouter] = {
    slug: CityFlowRouter(center_coords=city.center, radius=city.radius_meters)
    for slug, city in CITIES.items()
}


def _resolve_router(slug: str | None) -> CityFlowRouter:
    chosen = slug if slug in routers else DEFAULT_CITY
    return routers[chosen]


@app.on_event("startup")
def warmup_graphs():
    for slug, router in routers.items():
        log.info("Warming up router for city '%s'...", slug)
        router.load_graph()


@app.get("/")
def health_check():
    return {"status": "CityFlow API Online", "cities": [slug for slug in CITIES]}


@app.get("/api/v1/cities")
def list_supported_cities():
    return {"default": DEFAULT_CITY, "cities": list_cities()}


@app.post("/api/v1/route")
def calculate_route(request: RouteRequest):
    router = _resolve_router(request.city)
    route_coords, distance, max_route_incline = router.get_route(request)

    if not route_coords:
        raise HTTPException(
            status_code=424,
            detail="Não foi possível encontrar uma rota segura com as restrições atuais.",
        )

    return {
        "status": "success",
        "city": get_city(request.city).slug if request.city else DEFAULT_CITY,
        "route_geometry": route_coords,
        "distance_meters": distance,
        "max_route_incline": max_route_incline,
    }


@app.post("/api/v1/snap-point")
def snap_point(request: SnapPointRequest):
    router = _resolve_router(request.city)
    result = router.snap_point(request.coords)

    if not result["valid"]:
        raise HTTPException(status_code=422, detail=result["message"])

    return {
        "status": "success",
        "city": get_city(request.city).slug if request.city else DEFAULT_CITY,
        "snapped_coords": result["snapped_coords"],
        "distance_meters": result["distance_meters"],
        "adjusted": result.get("adjusted", False),
    }
