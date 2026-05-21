import requests

API_URL = "http://127.0.0.1:8000/api/v1/route"


def run_stress_test():
    print("==================================================")
    print(" CITYFLOW INCLUSIVE - API STRESS TEST")
    print("==================================================\n")

    print("=> Scenario A (Wheelchair, max_incline=0.08)")
    payload_a = {
        "start_coords": [41.2954, -7.7451],
        "end_coords": [41.2982, -7.7420],
        "profile": {
            "profile_name": "wheelchair",
            "max_incline": 0.08,
            "min_width": 1.2,
            "avoid_stairs": True,
            "surface_preference": ["paved", "asphalt", "concrete"],
        },
    }

    response_a = requests.post(API_URL, json=payload_a)
    if response_a.status_code == 200:
        data = response_a.json()
        print(f"   [PASS] 200 OK. Route has {len(data['route_geometry'])} points.")
    else:
        print(f"   [FAIL] Expected 200, got {response_a.status_code}")

    print("\n=> Scenario B (min_width=1.5)")
    payload_b = {
        "start_coords": [41.2954, -7.7451],
        "end_coords": [41.2982, -7.7420],
        "profile": {
            "profile_name": "wheelchair",
            "max_incline": 0.08,
            "min_width": 1.5,
            "avoid_stairs": True,
            "surface_preference": ["paved", "asphalt", "concrete"],
        },
    }

    response_b = requests.post(API_URL, json=payload_b)
    if response_b.status_code == 200:
        print("   [PASS] 200 OK. The request was processed.")
    else:
        print(f"   [FAIL] Expected 200, got {response_b.status_code}")

    print("\n=> Scenario C (out-of-bounds destination, expect 424)")
    payload_c = {
        "start_coords": [41.296, -7.746],
        "end_coords": [-10.0, -10.0],
        "profile": {
            "profile_name": "wheelchair",
            "max_incline": 0.08,
            "min_width": 1.2,
            "avoid_stairs": True,
            "surface_preference": [],
        },
    }

    response_c = requests.post(API_URL, json=payload_c)
    if response_c.status_code == 424:
        print(f"   [PASS] {response_c.status_code} correctly returned.")
        print(f"          Detail: {response_c.json().get('detail')}")
    else:
        print(f"   [FAIL] Expected 424, got {response_c.status_code}.")


if __name__ == "__main__":
    run_stress_test()
