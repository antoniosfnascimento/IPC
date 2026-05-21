import requests

API_URL = "http://127.0.0.1:8000/api/v1/route"


def test_api():
    print("==================================================")
    print(" CITYFLOW INTEGRATION TEST (10 REQUESTS)")
    print("==================================================\n")

    start_point = [41.2954, -7.7451]
    end_point = [41.2982, -7.7420]

    test_cases = [
        {"name": "Case 1: Strict sensitivity (2% / no stairs)", "inc": 0.02, "width": 1.0, "stairs": True},
        {"name": "Case 2: Extreme width (2.0 m)", "inc": 0.15, "width": 2.0, "stairs": True},
        {"name": "Case 3: Senior standard (12% / 0.8 m / allow stairs)", "inc": 0.12, "width": 0.8, "stairs": False},
        {"name": "Case 4: Wheelchair standard (8% / 1.2 m / no stairs)", "inc": 0.08, "width": 1.2, "stairs": True},
        {"name": "Case 5: Sporty (15% / 0.6 m / no stairs)", "inc": 0.15, "width": 0.6, "stairs": True},
        {"name": "Case 6: Cargo bike (5% / 1.5 m / no stairs)", "inc": 0.05, "width": 1.5, "stairs": True},
        {"name": "Case 7: Ultra strict (1% / 2.5 m / no stairs)", "inc": 0.01, "width": 2.5, "stairs": True},
        {"name": "Case 8: Fully relaxed (15% / 0.5 m / allow stairs)", "inc": 0.15, "width": 0.5, "stairs": False},
        {"name": "Case 9: Long Vila Real route (8% / 1.0 m / no stairs)", "inc": 0.08, "width": 1.0, "stairs": True, "end": [41.3000, -7.7400]},
        {"name": "Case 10: Across the river (5% / 1.5 m / no stairs)", "inc": 0.05, "width": 1.5, "stairs": True, "end": [41.297, -7.735]},
    ]

    for i, tc in enumerate(test_cases, 1):
        payload = {
            "start_coords": start_point,
            "end_coords": tc.get("end", end_point),
            "profile": {
                "profile_name": f"test_{i}",
                "max_incline": tc["inc"],
                "min_width": tc["width"],
                "avoid_stairs": tc["stairs"],
                "surface_preference": ["paved", "asphalt", "concrete"],
            },
        }

        r = requests.post(API_URL, json=payload)

        if r.status_code == 200:
            body = r.json()
            dist = body.get("distance_meters", 0)
            pts = len(body.get("route_geometry", []))
            grade = body.get("max_route_incline", 0) * 100
            print(f"[{i:02d}] {tc['name']}")
            print(f"     => [200 OK] distance={dist:.1f} m | nodes={pts} | peak slope={grade:.1f}%")
        elif r.status_code == 424:
            print(f"[{i:02d}] {tc['name']}")
            print(f"     => [424] No route is mathematically viable under these constraints.")
        else:
            print(f"[{i:02d}] {tc['name']}")
            print(f"     => [FAIL] Status {r.status_code}")

    print("\n[SUCCESS] 10 integration tests done.")


if __name__ == "__main__":
    test_api()
