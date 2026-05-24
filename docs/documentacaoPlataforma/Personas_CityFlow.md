# Personas (CityFlow)

Com base nas funcionalidades diferenciadoras da aplicação **CityFlow** e na análise sociodemográfica dos públicos-alvo da UC de Interação Pessoa-Computador (IPC), as três personas seguintes representam os utilizadores críticos (*edge cases*) em torno dos quais a interface e o algoritmo foram construídos.

| Nome / Idade | Limitação principal | Necessidade primária no CityFlow | Frustração com mapas convencionais |
| :--- | :--- | :--- | :--- |
| **João**, 34 | **Motora** — utilizador de cadeira de rodas manual. | Caminhos com inclinação controlada e evasão rigorosa de passeios sem rebaixamento, escadas e pavimentos de terra solta. | Os mapas convencionais mandam-no pelo caminho "mais rápido". Esse caminho frequentemente esconde uma colina íngreme que o exausta ou empurra-o para calçada antiga impraticável — acaba a recuar e a desperdiçar energia. |
| **Maria**, 72 | **Sensorial (visão reduzida) e física (fadiga)** — sénior com cataratas parciais que se desloca apoiada por bengala. | Navegar com interface limpa, botões grandes e priorizar distâncias planas que exijam pouco esforço respiratório. | A interface está cheia de informação irrelevante (restaurantes, hotéis). A letra é minúscula. Os mapas nunca a avisam sobre obras no passeio, que a obrigam a correr riscos pela estrada. |
| **Ricardo**, 45 | **Cognitivo-sensorial** — daltónico (Deuteranopia, dificuldade no eixo verde/vermelho). | Ler o mapa através de contrastes dinâmicos, padrões visuais óbvios ou feedback háptico (vibração) quando se desvia da direção. | Linhas de rota vermelhas sobre uma topografia verde misturam-se. Não distingue de relance uma via de trânsito rápido de uma rua pedonal secundária. Faltam avisos multimodais para rotas alternativas. |

### Como as personas se refletem na app

| Persona | Decisão de design no MVP entregue |
| :--- | :--- |
| João | Slider `Inclinação máxima` (2 %–15 %) + slider `Largura mínima da via` (0,5 m–2,0 m) + *toggle* `Evitar escadas`. O motor aplica multiplicador ×15 quando o limite é excedido e ×3 quando está próximo. O painel de resultado mostra inclinação crítica com *badge* verde/vermelho para confirmar/avisar. |
| Maria | UI condensada na sidebar (sem campos de texto exigentes — basta clicar no mapa). Tipografia em `text-sm`/`text-base` (passível de zoom até 200 %). Botão "Calcular rota segura" com ~56 px de altura. Mensagens de erro com `role="alert"`. |
| Ricardo | Linha da rota num azul forte (`#2563eb`) sobre basemap claro — alto contraste em qualquer eixo de daltonismo comum. Marcadores de partida (casa) e destino (bandeira) com **formas** distintas, não apenas cores. Estado da inclinação combina cor com **ícone** (`CheckCircle` / `AlertTriangle`). |

Estas personas justificam a existência das variáveis `max_incline`, `min_width`, `avoid_stairs` e do *snap-point* pedonal. O modo *Easy Read* dedicado, o alto contraste explícito e o feedback háptico/sonoro ficam preservados no *roadmap* (ver `Requisitos_Funcionais.md` e `User_Journey_Joao.md`).
