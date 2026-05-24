# Cenários de Teste e Aceitação para as Regras de Negócio de *Routing* (QA)

Para garantir que o motor matemático do CityFlow e as métricas de penalização (dicionário de dados e lógica matemática) funcionam corretamente num contexto real, a equipa de QA deve validar o algoritmo contra os seis cenários-limite seguintes.

Estes testes provam que o sistema cumpre a sua proposta de valor MVP: dar primazia à *viabilidade física* sobre a *distância*. A coluna **Estado** indica se o cenário está coberto pelos testes automáticos / manuais do MVP entregue (✅) ou se depende de funcionalidade em *roadmap* (🔜).

---

## Cenário 1 — Resistência e declive elevado (Vila Real) ✅
**Perfil:** utilizador de cadeira de rodas manual (forte restrição motora, baixa tolerância cardíaca).
**Objetivo:** viajar do centro de Vila Real (Avenida Carvalho Araújo) até à zona da UTAD.
**Variáveis ativas:** `max_incline: 0.08` (8 %). `avoid_stairs: True`.
**Critérios de aceitação:**
1. O algoritmo **não pode** escolher ruas mais íngremes do que 8 %, mesmo que sejam o caminho mais curto em linha reta.
2. O caminho gerado deve fazer ziguezagues pelas curvas de nível (ruas transversais) para anular a elevação do terreno, evidenciando o multiplicador ×15.
3. *Pass criterion:* o comprimento total tem de ser visivelmente maior e comprovadamente viável face à distância em linha reta.
4. Se nenhuma rota satisfizer as restrições, a API deve devolver 424 e o frontend mostrar mensagem amigável.

---

## Cenário 2 — Caminho morto e filtro estrito de superfície ✅
**Perfil:** sénior com mobilidade reduzida (usa andarilho).
**Objetivo:** atravessar a parte histórica empedrada da cidade.
**Variáveis ativas:** `surface_preference: ['paved', 'asphalt']`, excluindo `cobblestone` explicitamente. `max_incline: 0.12`.
**Critérios de aceitação:**
1. O sistema tem de preferir asfalto liso. Se o único acesso direto for maioritariamente em calçada, a rota deve evitar essa artéria sempre que possível.
2. A rota deve contornar as praças com calçada portuguesa (penalização ×3,5).
3. *Fallback:* se as únicas ruas dos últimos 100 m forem em calçada, o sistema não pode crashar; devolve uma rota que minimiza a exposição à calçada e mostra o alerta de inclinação crítica se aplicável.

---

## Cenário 3 — Tolerância ao declive (Paris) ✅
**Perfil:** utilizador com perfil relaxado (passo livre).
**Objetivo:** mover-se entre dois pontos do centro de Paris (Châtelet → Marais) onde Paris tem mapeamento de `smoothness` denso (31,5 % das arestas).
**Variáveis ativas:** `max_incline: 0.15` (15 %). `avoid_stairs: False`.
**Critérios de aceitação:**
1. Cada mexida nos sliders deve produzir uma rota visivelmente diferente (efeito direto da densidade do *tagging* em Paris).
2. A inclinação crítica reportada não pode exceder o cap interno de 25 % (proteção contra ruído do DEM em arestas curtas).
3. O *snap* dos pontos A/B deve aceitar cliques perto do rio Sena ou em parques (Tuileries), redirecionando para a aresta pedonal mais próxima.

---

## Cenário 4 — *Crowdsourcing* em tempo real 🔜
**Perfil:** qualquer utilizador com limitações físicas.
**Objetivo:** percurso matinal habitual que atravessa uma ponte estreita.
**Variáveis ativas:** `POST /api/v1/report-barrier` foi disparado. Uma barreira `is_blocked: True` foi colocada 30 min antes, exatamente na ponte.
**Critérios de aceitação:**
1. O algoritmo atinge a secção onde `is_blocked = True` foi injetado na RAM e a penalização de 99999 entra em ação.
2. O algoritmo fecha a via e desvia o utilizador antes do obstáculo.
3. Se essa via for a única entrada terrestre, a API responde com um erro semântico de negócio em vez de tentar chamadas vazias em loop.

> **Estado MVP:** o endpoint `report-barrier` é uma extensão planeada do contrato da API. O motor já tem a heurística de `is_blocked` no `_calculate_edge_weight`; falta o caminho de entrada via API e o botão na UI.

---

## Cenário 5 — Robustez contra tags em falta ✅
**Perfil:** carrinho de bebé duplo ou cadeira de rodas motorizada (largura extra).
**Objetivo:** caminhar entre duas casas numa zona residencial periférica.
**Variáveis ativas:** `min_width: 1.25 m`.
**Critérios de aceitação:**
1. O motor encontra arestas residenciais sem a tag `width` no OSM (~98 % das arestas em Vila Real).
2. O `FeatureSanitizer` entra em ação e impede um 500 (Pydantic ValueError) ou um crash do Python em `None < 1.25`.
3. A largura conservadora *default* (0,5 m) garante que arestas sem tag são penalizadas em ×5 por segurança.

---

## Cenário 6 — Coordenadas fora da rede pedonal ✅
**Perfil:** qualquer.
**Objetivo:** validar a robustez do *snap-point*.
**Variáveis ativas:** N/A. O utilizador clica num ponto sem rua pedonal a menos de 250 m (ex.: meio de um parque grande, autoestrada, rio).
**Critérios de aceitação:**
1. A API responde com `HTTP 422` e uma mensagem indicando a distância à rua pedonal mais próxima.
2. O frontend mostra o alerta vermelho e não coloca marcador.
3. O ponto não é projetado sobre vias automóveis (motorway, trunk) — o *snap subgraph* exclui esses tipos.

---

## Como reproduzir

Os cenários ✅ podem ser executados via:
*   `backend/integration_validator.py` para uma bateria de 10 perfis em Vila Real.
*   `backend/stress_test_api.py` para os três cenários principais.
*   Validação manual no browser para os fluxos de UI/UX.
