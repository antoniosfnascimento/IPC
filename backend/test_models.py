from pydantic import ValidationError

from models import RouteRequest, UserProfile
from sanitizer import FeatureSanitizer


def test_sanitizer():
    print("--- Teste ao FeatureSanitizer ---")

    print(f"Teste largura None -> {FeatureSanitizer.sanitize_width(None)} m")
    print(f"Teste largura ''   -> {FeatureSanitizer.sanitize_width('')} m")
    print(f"Teste '1.5'        -> {FeatureSanitizer.sanitize_width('1.5')} m")
    print(f"Teste '2,5'        -> {FeatureSanitizer.sanitize_width('2,5')} m")
    print(f"Teste '1.2m'       -> {FeatureSanitizer.sanitize_width('1.2m')} m")
    print(f"Teste '-1'         -> {FeatureSanitizer.sanitize_width('-1')} m")


def test_models():
    print("\n--- Teste aos modelos Pydantic ---")

    try:
        profile = UserProfile(
            profile_name="wheelchair",
            max_incline=0.08,
            min_width=1.2,
            avoid_stairs=True,
            surface_preference=["paved", "asphalt"],
        )
        print("UserProfile válido:")
        print(profile.model_dump_json(indent=2))

        request = RouteRequest(
            start_coords=(41.2954, -7.7451),
            end_coords=(41.2982, -7.7420),
            profile=profile,
        )
        print("RouteRequest válido aceite.")
    except ValidationError as e:
        print("Erro de validação inesperado:", e)

    try:
        print("\nA tentar criar um perfil inválido (string em max_incline)...")
        UserProfile(
            profile_name="wheelchair",
            max_incline="not_a_number",
            min_width=1.2,
            avoid_stairs=True,
            surface_preference=[],
        )
    except ValidationError as e:
        print("Erro de validação apanhado, como esperado:")
        print(e)


if __name__ == "__main__":
    test_sanitizer()
    test_models()
