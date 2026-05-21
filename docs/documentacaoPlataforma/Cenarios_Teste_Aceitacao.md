# Cenários de Teste e Aceitação para as Regras de Negócio de *Routing* (QA)

Para garantir que o motor matemático do CityFlow e as métricas de penalização (dicionário de dados e lógica matemática) funcionam corretamente num contexto real, a equipa de QA deve validar o algoritmo contra os cinco cenários-limite seguintes.

Estes testes provam que o sistema cumpre a sua proposta de valor MVP: dar primazia à *viabilidade física* sobre a *distância*.

---

## Cenário 1 — Resistência e declive elevado
**Perfil:** utilizador de cadeira de rodas manual (forte restrição motora, baixa tolerância cardíaca).
**Objetivo:** viajar da "Câmara Municipal de Vila Real" até ao "Terminal Rodoviário".
**Variáveis ativas:** `max_incline: 0.08` (8 %). `avoid_stairs: True`.
**Critérios de aceitação:**
1. O algoritmo **não pode** escolher ruas mais íngremes do que 8 %, mesmo que sejam o caminho mais curto em linha reta.
2. O caminho gerado deve fazer ziguezagues pelas curvas de nível (ruas transversais) para anular a elevação do terreno, evidenciando o multiplicador ×15.
3. *Pass criterion:* o comprimento total (ex.: 2,1 km) tem de ser visivelmente maior e comprovadamente viável face à distância em linha reta (ex.: 800 m).

---

## Cenário 2 — Caminho morto e filtro estrito de superfície
**Perfil:** sénior com mobilidade reduzida (usa andarilho).
**Objetivo:** atravessar a parte histórica empedrada da cidade até à Sé.
**Variáveis ativas:** `surface_preference: ['paved', 'asphalt']`, excluindo `cobblestone` explicitamente. `max_incline: 0.12`.
**Critérios de aceitação:**
1. O sistema tem de preferir asfalto liso. Se o único acesso direto à Sé for maioritariamente em calçada, a rota deve evitar essa artéria.
2. A rota deve contornar as praças com calçada portuguesa (penalização ×3,5) sempre que possível.
3. *Fallback:* se as únicas ruas dos últimos 100 m antes da Sé forem em calçada, o sistema não pode crashar (HTTP 424); em vez disso, devolve uma rota que minimiza a exposição à calçada e mostra o alerta "piso irregular no último troço".

---

## Cenário 3 — Tolerância ao declive (baixa visão)
**Perfil:** utilizador de baixa visão (usa bengala tátil).
**Objetivo:** mover-se das residências universitárias até ao limite sul do campus da UTAD (terreno muito íngreme).
**Variáveis ativas:** `max_incline: 0.20` (20 %). Penalização de passadeiras ativa.
**Critérios de aceitação:**
1. A rota não pode contornar quarteirões só por causa da elevação. Com tolerância de 20 %, o caminho deve assemelhar-se a uma linha reta.
2. O sistema deve detetar rotundas perigosas (trânsito rápido, passadeiras sem sinalização eletrónica ou ilha tátil) e desviar-se por passagens desniveladas ou passadeiras com sinal sonoro (penalização ×10), ignorando a distância.

---

## Cenário 4 — *Crowdsourcing* em tempo real
**Perfil:** qualquer utilizador com limitações físicas.
**Objetivo:** percurso matinal habitual (A → B) que atravessa uma ponte estreita.
**Variáveis ativas:** `POST /api/v1/report-barrier` foi disparado. Uma barreira `is_blocked: True` foi colocada 30 min antes, exatamente na ponte.
**Critérios de aceitação:**
1. O algoritmo atinge a secção onde `is_blocked = True` foi injetado na RAM e a penalização de 99999 entra em ação.
2. O algoritmo fecha a via e desvia o utilizador antes do obstáculo.
3. Se essa via for a única entrada terrestre (criando um nó isolado), a API responde com um erro semântico de negócio ("caminho intercetado por obstáculo, sem rotas alternativas até remoção"), em vez de tentar chamadas vazias em loop.

---

## Cenário 5 — Robustez contra tags em falta
**Perfil:** carrinho de bebé duplo ou cadeira de rodas motorizada (largura extra).
**Objetivo:** caminhar entre duas casas numa zona residencial periférica.
**Variáveis ativas:** `min_width: 1.25 m`.
**Critérios de aceitação:**
1. O motor encontra arestas residenciais sem a tag `width` no OSM.
2. O `FeatureSanitizer` entra em ação e impede um 500 (Pydantic ValueError) ou um crash do Python em `None < 1.25`.
3. A largura conservadora *default* (1,0 m) garante que 1,0 < 1,25 ⇒ a aresta sem tag é rejeitada por segurança, evitando que o utilizador encalhe entre muros estreitos.
