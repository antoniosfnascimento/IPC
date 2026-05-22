from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import RouteRequest, SnapPointRequest
from engine.router import CityFlowRouter

app = FastAPI(title="CityFlow Inclusivo API", version="1.1")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



city_router = CityFlowRouter(center_coords=(41.296, -7.746), radius=1500)


@app.get("/")
def health_check():
    return {"status": "CityFlow API Online"}


@app.post("/api/v1/route")
def calculate_route(request: RouteRequest):
    
    result = city_router.get_route(request)
    
    if isinstance(result, tuple) and len(result) == 3:
        route_coords, distance, max_route_incline = result
    else:
        route_coords, distance, max_route_incline = result, 0.0, 0.0
    
    if not route_coords:
        raise HTTPException(
            status_code=424, 
            detail="Não foi possível encontrar uma rota segura com as restrições atuais."
        )
        
    return {
        "status": "success",
        "route_geometry": route_coords,
        "distance_meters": distance,
        "max_route_incline": max_route_incline
    }


@app.post("/api/v1/snap-point")
def snap_point(request: SnapPointRequest):
    result = city_router.snap_point(request.coords)

    if not result["valid"]:
        raise HTTPException(
            status_code=422,
            detail=result["message"]
        )

    return {
        "status": "success",
        "snapped_coords": result["snapped_coords"],
        "distance_meters": result["distance_meters"]
    }
