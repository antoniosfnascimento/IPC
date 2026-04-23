from models import UserProfile, RouteRequest
from engine.router import CityFlowRouter
import sys

def run_test():
    print("--- Testing Routing Engine (CityFlowRouter) ---")
    
    
    profile = UserProfile(
        profile_name="wheelchair",
        max_incline=0.08,
        min_width=1.2,
        avoid_stairs=True,
        surface_preference=["paved", "asphalt", "concrete"]
    )
    
    
    
    request = RouteRequest(
        start_coords=(41.2954, -7.7451),
        end_coords=(41.2982, -7.7420),
        profile=profile
    )
    
    
    router = CityFlowRouter(center_coords=(41.296, -7.746), radius=1500)
    
    
    print("A iniciar o cálculo da rota. Isto vai requerer o download dos dados OSM caso a cache esteja vazia...")
    route_coords = router.get_route(request)
    
    if route_coords:
        print(f"\n=> Rota calculada com sucesso com {len(route_coords)} pontos de navegação.")
        print("Coordenadas geradas:")
        for idx, coord in enumerate(route_coords):
            print(f"  [{idx}] -> Lat: {coord[0]:.6f}, Lon: {coord[1]:.6f}")
    else:
        print("\n=> Falha: Nenhuma rota encontrada!")
        sys.exit(1)

if __name__ == "__main__":
    run_test()
