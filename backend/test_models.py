from pydantic import ValidationError

from models import RouteRequest, UserProfile
from sanitizer import FeatureSanitizer


def test_sanitizer():
    print("--- Testing FeatureSanitizer ---")

    print(f"Test None width -> {FeatureSanitizer.sanitize_width(None)} m")
    print(f"Test '' width   -> {FeatureSanitizer.sanitize_width('')} m")
    print(f"Test '1.5'      -> {FeatureSanitizer.sanitize_width('1.5')} m")
    print(f"Test '2,5'      -> {FeatureSanitizer.sanitize_width('2,5')} m")
    print(f"Test '1.2m'     -> {FeatureSanitizer.sanitize_width('1.2m')} m")
    print(f"Test '-1'       -> {FeatureSanitizer.sanitize_width('-1')} m")


def test_models():
    print("\n--- Testing Pydantic models ---")

    try:
        profile = UserProfile(
            profile_name="wheelchair",
            max_incline=0.08,
            min_width=1.2,
            avoid_stairs=True,
            surface_preference=["paved", "asphalt"],
        )
        print("Valid UserProfile:")
        print(profile.model_dump_json(indent=2))

        request = RouteRequest(
            start_coords=(41.2954, -7.7451),
            end_coords=(41.2982, -7.7420),
            profile=profile,
        )
        print("Valid RouteRequest accepted.")
    except ValidationError as e:
        print("Unexpected validation error:", e)

    try:
        print("\nTrying to create an invalid profile (string for incline)...")
        UserProfile(
            profile_name="wheelchair",
            max_incline="not_a_number",
            min_width=1.2,
            avoid_stairs=True,
            surface_preference=[],
        )
    except ValidationError as e:
        print("Validation error caught as expected:")
        print(e)


if __name__ == "__main__":
    test_sanitizer()
    test_models()
