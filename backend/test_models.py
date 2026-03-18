from models import UserProfile, RouteRequest
from sanitizer import FeatureSanitizer
from pydantic import ValidationError

def test_sanitizer():
    print("--- Testing FeatureSanitizer ---")
    
    # Test 1: Null width
    w1 = FeatureSanitizer.sanitize_width(None)
    print(f"Test None width -> {w1}m")
    
    # Test 2: Empty width
    w2 = FeatureSanitizer.sanitize_width("")
    print(f"Test Empty width -> {w2}m")
    
    # Test 3: Standard float string
    w3 = FeatureSanitizer.sanitize_width("1.5")
    print(f"Test '1.5' -> {w3}m")
    
    # Test 4: Comma separated decimal (requested by user)
    w4 = FeatureSanitizer.sanitize_width("2,5")
    print(f"Test '2,5' -> {w4}m")
    
    # Test 5: With metric units
    w5 = FeatureSanitizer.sanitize_width("1.2m")
    print(f"Test '1.2m' -> {w5}m")

    # Test 6: Invalid/negative width
    w6 = FeatureSanitizer.sanitize_width("-1")
    print(f"Test '-1' -> {w6}m")

def test_models():
    print("\n--- Testing Pydantic Models ---")
    
    try:
        profile = UserProfile(
            profile_name="wheelchair",
            max_incline=0.08,
            min_width=1.2,
            avoid_stairs=True,
            surface_preference=["paved", "asphalt"]
        )
        print("Valid UserProfile created successfully:")
        print(profile.model_dump_json(indent=2))
        
        request = RouteRequest(
            start_coords=(41.2954, -7.7451),
            end_coords=(41.2982, -7.7420),
            profile=profile
        )
        print("Valid RouteRequest created successfully.")
    except ValidationError as e:
        print("Unexpected validation error:", e)
        
    try:
        print("\nAttempting to create invalid profile (string for incline)...")
        # Should fail if max_incline gets a string that can't be coerced or if coercion is strict
        # But Pydantic will actually coerce "0.08" to float if it can. Let's send a completely invalid string.
        UserProfile(
            profile_name="wheelchair",
            max_incline="not_a_number", 
            min_width=1.2,
            avoid_stairs=True,
            surface_preference=[]
        )
    except ValidationError as e:
        print("Successfully caught ValidationError:")
        print(e)
        
if __name__ == "__main__":
    test_sanitizer()
    test_models()
