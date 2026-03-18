import requests
import json

API_URL = "http://127.0.0.1:8000/api/v1/route"

def run_stress_test():
    print("==================================================")
    print(" INICIANDO STRESS TEST API: CITYFLOW INCLUSIVO")
    print("==================================================\n")
    
    # ---------------------------------------------------------
    # CENÁRIO A: Rota Inclusiva Standard
    # ---------------------------------------------------------
    print("=> Cenário A (Inclusividade: wheelchair, max_incline: 0.08)")
    payload_a = {
        "start_coords": [41.2954, -7.7451],
        "end_coords": [41.2982, -7.7420],
        "profile": {
            "profile_name": "wheelchair",
            "max_incline": 0.08,
            "min_width": 1.2,
            "avoid_stairs": True,
            "surface_preference": ["paved", "asphalt", "concrete"]
        }
    }
    
    response_a = requests.post(API_URL, json=payload_a)
    if response_a.status_code == 200:
        data = response_a.json()
        print(f"   [PASS] Status 200 OK. Rota calculada com {len(data['route_geometry'])} pontos.")
    else:
        print(f"   [FAIL] Esperado 200, obtido {response_a.status_code}")
        
    # ---------------------------------------------------------
    # CENÁRIO B: Defesa 0.5m
    # ---------------------------------------------------------
    print("\n=> Cenário B (Defesa 0.5m: min_width = 1.5)")
    payload_b = {
        "start_coords": [41.2954, -7.7451],
        "end_coords": [41.2982, -7.7420],
        "profile": {
            "profile_name": "wheelchair",
            "max_incline": 0.08,
            "min_width": 1.5,
            "avoid_stairs": True,
            "surface_preference": ["paved", "asphalt", "concrete"]
        }
    }
    
    response_b = requests.post(API_URL, json=payload_b)
    if response_b.status_code == 200:
        print("   [PASS] Status 200 OK. O pedido foi processado.")
        print("          NOTA: Verifique o terminal do servidor uvicorn para confirmar os logs de aviso '0.5m'.")
    else:
        print(f"   [FAIL] Esperado 200, obtido {response_b.status_code}")

    # ---------------------------------------------------------
    # CENÁRIO C: Status 424 via restrições impossíveis ou pontos isolados
    # ---------------------------------------------------------
    print("\n=> Cenário C (Teste de Erro / 424 Failed Dependency)")
    # Forçar a procura de rota entre pontos num grafo que não têm ligação,
    # ou usando coordenadas distantes que vão fazer snap a componentes disjuntos na periferia.
    payload_c = {
        "start_coords": [41.296, -7.746],
        "end_coords": [-10.0, -10.0],  # Força snap para os limites distantes do grafo
        "profile": {
            "profile_name": "wheelchair",
            "max_incline": 0.08,
            "min_width": 1.2,
            "avoid_stairs": True,
            "surface_preference": []
        }
    }
    
    response_c = requests.post(API_URL, json=payload_c)
    if response_c.status_code == 424:
        print(f"   [PASS] Status {response_c.status_code} corretamente devolvido pela API.")
        print(f"          Detalhe: {response_c.json().get('detail')}")
    else:
        print(f"   [FAIL] Esperado 424, mas obtido {response_c.status_code}.")
        if response_c.status_code == 200:
            print("          A biblioteca de roteamento conseguiu encontrar um caminho mesmo para nós distantes (fallback ao componente principal).")

if __name__ == "__main__":
    run_stress_test()
