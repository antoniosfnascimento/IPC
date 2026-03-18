# Cenários de Teste e Aceitação de Regras de Negócio (QA Routing)

Para garantir que o motor matemático do "CityFlow Inclusivo" e as métricas de penalização (Dicionário de Dados e Lógica Matemática) estão a ser corretamente aplicados em contexto real, a equipa de QA (Quality Assurance) deve validar o algoritmo contra os seguintes 5 cenários extremos.

Estes testes validam que o sistema cumpre a sua proposta de valor (MVP): dar primazia à "Viabilidade Física" sobre a "Distância".

---

## Cenário 1: Teste de Resistência e Declive Elevado
**Perfil:** Usuário em Cadeira de Rodas Manual (Forte restrição motora e baixa tolerância cardíaca).
**Objetivo:** Viagem da "Câmara Municipal de Vila Real" até ao "Terminal Rodoviário".
**Variáveis Ativas:** `max_incline: 0.08` (8%). `avoid_stairs: True`.
**Métricas de Sucesso (Acceptance Criteria):**
1. O algoritmo **não** pode selecionar ruas com inclinações acima de 8%, mesmo que representem o caminho retilíneo mais curto.
2. O caminho gerado deve formar ziguezagues pelas curvas de nível da encosta (ruas transversais) e marginalmente para anular a elevação do terreno, evidenciando o multiplicador x15 em inclinações elevadas. 
3. *Pass Criterion:* O comprimento total da rota gerada (ex: 2.1km) deve ser visivelmente superior (e comprovadamente viável) à distância em linha reta (ex: 800m).

---

## Cenário 2: Caminho Morto e Filtragem Restrita de Superfície
**Perfil:** Pessoa Idosa com Mobilidade Reduzida (Usa andarilho).
**Objetivo:** Cruzar a parte histórica e empedrada da cidade para chegar à Sé Catedral.
**Variáveis Ativas:** `surface_preference: ['paved', 'asphalt']`, excluindo explicitamente `cobblestone` (calçada portuguesa). `max_incline: 0.12`.
**Métricas de Sucesso (Acceptance Criteria):**
1. O sistema deve priorizar asfalto liso. Se o único acesso direto à Sé for maioritariamente em calçada irregular (`cobblestone`), a rota deve evitar essa artéria.
2. A rota deve circundar as praças com calçada portuguesa (Penalização x3.5) até ao limite mínimo possível.
3. *Fallback Criterion:* Se as *únicas* vias na vizinhança final de 100m da Sé forem calçada, o sistema não deve crashar (regressando HTTP 424), mas sim entregar um traçado que minimiza ao máximo a permanência em passeios irregulares e exibe um alerta de "Piso irregular no último trecho".

---

## Cenário 3: Tolerância Visuo-Hormonal a Declive (Baixa Visão)
**Perfil:** Pessoa com Baixa Visão / Invisibilidade (Usa bengala tátil).
**Objetivo:** Mover-se desde as Residências Universitárias até ao limite sul do Campus da UTAD (terreno extremamente montanhoso).
**Variáveis Ativas:** `max_incline: 0.20` (20%). Penalização de passadeiras ativada.
**Métricas de Sucesso (Acceptance Criteria):**
1. A rota não deve apresentar desvios anormais de contorno de quarteirão só por causa do relevo. Dada a tolerância de 20%, o traçado deve ser equiparável a uma linha reta normal.
2. O sistema deve detetar rotundas perigosas (vias de trânsito rápido com passadeiras sem sinalização eletrónica e sem "ilha" de segurança tátil) e redesenhar o caminho por passagens desniveladas ou passadeiras dotadas de piso rebaixado/sinal sonoro (Penalização x10.0), ignorando totalmente distâncias.

---

## Cenário 4: Interações Críticas de Crowdsourcing em Tempo Real
**Perfil:** Qualquer utilizador com limitações físicas.
**Objetivo:** Caminho habitual matinal (Origem A -> Destino B) que passa numa única ponte / corredor apertado de acesso único.
**Variáveis Ativas:** Utilização do Endpoint `POST /api/v1/report-barrier`. Foi submetida uma barreira de obras (`is_blocked: True`) 30 minutos antes e posicionada exatamente no centro dessa ponte.
**Métricas de Sucesso (Acceptance Criteria):**
1. O algoritmo atinge a secção onde a tag `is_blocked = True` foi temporariamente introduzida na RAM e o multiplicador astronómico de penalidade (99999.0) entra em ação.
2. O algoritmo **encerra a via** e desvia o condutor imediatamente antes do obstáculo.
3. Se essa via for a *única* entrada terrestre possível (criando um nó isolado verdadeiro), a API tem de responder liminarmente com erro semântico de negócio: "Caminho intercetado por obstáculo. Sem rotas alternativas até remoção." em vez de tentar empilhar chamadas vazias em loop.

---

## Cenário 5: Robustez contra Falta de Tags Base de Dados (Largura)
**Perfil:** Carrinho de Bebé Duplo ou Cadeira de Rodas Motorizada (Largura Excecional Carga Eixo).
**Objetivo:** Caminhar entre duas habitações numa zona residencial mais periférica da cidade.
**Variáveis Ativas:** `min_width: 1.25m`.
**Métricas de Sucesso (Acceptance Criteria):**
1. O motor encontra arestas residenciais que não têm a tag OSM `width` mapeada pelos cartógrafos. 
2. A aplicação do método `FeatureSanitizer` (definido no modelo) atua e não emite um Erro 500 do Pydantic (ValueError) ou quebra matemática na comparação (`None < 1.25` geraria crash no Python).
3. O script deve substituir os nulos `None` com o default conservador (Ex: Vias locais classificadas como pedonais assumem `width=1.0m`. Assim, porque 1.0 < 1.25, a via não mapeada é rejeitada por precaução de segurança face a encravamento da máquina com muros estreitos).
