import sys

from engine.router import CityFlowRouter
from models import RouteRequest, UserProfile


def run_test():
    print("--- Testing CityFlowRouter ---")

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

    print("Computing the route. OSM data will be downloaded on the first run...")
    coords, distance, max_grade = router.get_route(request)

    if coords:
        print(f"\n=> Route found with {len(coords)} navigation points.")
        print(f"   Distance: {distance:.1f} m | peak slope: {max_grade * 100:.1f}%")
    else:
        print("\n=> Failure: no route found.")
        sys.exit(1)


if __name__ == "__main__":
    run_test()
