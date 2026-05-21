import requests

API_URL = "http://127.0.0.1:8000/api/v1/route"


def test_api():
    print("==================================================")
    print(" CITYFLOW — TESTE DE INTEGRAÇÃO (10 PEDIDOS)")
    print("==================================================\n")

    start_point = [41.2954, -7.7451]
    end_point = [41.2982, -7.7420]

    test_cases = [
        {"name": "Caso 1: Sensibilidade extrema (2% / sem escadas)", "inc": 0.02, "width": 1.0, "stairs": True},
        {"name": "Caso 2: Largura extrema (2,0 m)", "inc": 0.15, "width": 2.0, "stairs": True},
        {"name": "Caso 3: Padrão sénior (12% / 0,8 m / com escadas)", "inc": 0.12, "width": 0.8, "stairs": False},
        {"name": "Caso 4: Padrão cadeira de rodas (8% / 1,2 m / sem escadas)", "inc": 0.08, "width": 1.2, "stairs": True},
        {"name": "Caso 5: Atleta (15% / 0,6 m / sem escadas)", "inc": 0.15, "width": 0.6, "stairs": True},
        {"name": "Caso 6: Bicicleta de carga (5% / 1,5 m / sem escadas)", "inc": 0.05, "width": 1.5, "stairs": True},
        {"name": "Caso 7: Ultra estrito (1% / 2,5 m / sem escadas)", "inc": 0.01, "width": 2.5, "stairs": True},
        {"name": "Caso 8: Totalmente relaxado (15% / 0,5 m / com escadas)", "inc": 0.15, "width": 0.5, "stairs": False},
        {"name": "Caso 9: Rota longa em Vila Real (8% / 1,0 m / sem escadas)", "inc": 0.08, "width": 1.0, "stairs": True, "end": [41.3000, -7.7400]},
        {"name": "Caso 10: Atravessar o rio (5% / 1,5 m / sem escadas)", "inc": 0.05, "width": 1.5, "stairs": True, "end": [41.297, -7.735]},
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
            print(f"     => [200 OK] distância={dist:.1f} m | nós={pts} | declive crítico={grade:.1f}%")
        elif r.status_code == 424:
            print(f"[{i:02d}] {tc['name']}")
            print(f"     => [424] Não existe rota viável com estas restrições.")
        else:
            print(f"[{i:02d}] {tc['name']}")
            print(f"     => [FAIL] Estado {r.status_code}")

    print("\n[SUCESSO] 10 testes de integração concluídos.")


if __name__ == "__main__":
    test_api()
