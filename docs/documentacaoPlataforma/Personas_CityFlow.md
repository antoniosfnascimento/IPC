# Personas e Casos de Uso (CityFlow)

Com base nas funcionalidades diferenciadoras da aplicação **CityFlow** e na análise sociodemográfica dos públicos-alvo da UC de Interação Pessoa-Computador (IPC), as Personas seguintes representam os utilizadores críticos (*edge cases*) em torno dos quais a interface e o algoritmo de mapas foram construídos.

| Nome / Idade | Limitação principal (perfil) | Necessidade primária no CityFlow | Frustração comum com mapas convencionais (Google Maps / Apple Maps) |
| :--- | :--- | :--- | :--- |
| **João**, 34 | **Motora:** utilizador de cadeira de rodas manual. | Caminhos com inclinação controlada e evasão rigorosa de passeios sem rebaixamento, escadas e pavimentos de terra solta. | Os mapas convencionais mandam-no pelo caminho "mais rápido". Esse caminho frequentemente esconde uma colina íngreme que o exausta ou empurra-o para calçada antiga impraticável — acaba a recuar e a desperdiçar energia. |
| **Maria**, 72 | **Sensorial (visão reduzida) e física (fadiga):** sénior com cataratas parciais que se desloca apoiada por bengala. | Navegar em modo *Easy Read* (interface limpa), com botões grandes e priorizar distâncias planas que exijam pouco esforço respiratório. | A interface está cheia de informação irrelevante (restaurantes, hotéis). A letra é minúscula. Os mapas nunca a avisam sobre obras no passeio (sem *crowdsourcing*), que a obrigam a correr riscos pela estrada. |
| **Ricardo**, 45 | **Cognitivo-sensorial:** daltónico (Deuteranopia — dificuldade no eixo verde/vermelho). | Ler o mapa através de contrastes dinâmicos, padrões visuais óbvios ou feedback háptico (vibração) quando se desvia da direção. | Linhas de rota vermelhas sobre uma topografia verde misturam-se. Não distingue de relance uma via de trânsito rápido de uma rua pedonal secundária. Faltam avisos multimodais para rotas alternativas. |

Estas Personas reforçam a existência das variáveis `max_incline`, `avoid_stairs` e do modo *Easy Read*, além da funcionalidade extra de *crowdsourcing* de obstáculos na via, que constituem as fundações do CityFlow.
