import sys

from engine.router import CityFlowRouter
from models import RouteRequest, UserProfile


def run_test():
    print("--- Teste ao CityFlowRouter ---")

    profile = UserProfile(
        profile_name="wheelchair",
        max_incline=0.08,
        min_width=1.2,
        avoid_stairs=True,
        surface_preference=["paved", "asphalt", "concrete"],
    )

    request = RouteRequest(
        start_coords=(41.2954, -7.7451),
        end_coords=(41.2982, -7.7420),
        profile=profile,
    )

    router = CityFlowRouter(center_coords=(41.296, -7.746), radius=1500)

    print("A calcular a rota. Os dados OSM serão descarregados na primeira execução...")
    coords, distance, max_grade = router.get_route(request)

    if coords:
        print(f"\n=> Rota encontrada com {len(coords)} pontos de navegação.")
        print(f"   Distância: {distance:.1f} m | declive crítico: {max_grade * 100:.1f}%")
    else:
        print("\n=> Falha: não foi encontrada uma rota.")
        sys.exit(1)


if __name__ == "__main__":
    run_test()
