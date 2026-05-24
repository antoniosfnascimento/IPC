# Tabela de Requisitos Funcionais (CityFlow MVP)

Esta tabela sintetiza a documentação arquitetural do CityFlow num formato de *Product Backlog* focado no Mínimo Produto Viável (MVP), priorizando o núcleo de acessibilidade técnica face às abstrações de negócio.

A coluna **Estado** indica se o requisito está efetivamente implementado na versão entregue do MVP (✅), parcialmente coberto (🟡) ou planeado para uma fase posterior (🔜).

| ID | Funcionalidade | Descrição técnica (implementação) | Prioridade | Estado |
| :---: | :--- | :--- | :---: | :---: |
| **RF-01** | Seleção de perfil de acessibilidade | A sidebar do frontend mantém em estado React três variáveis — `maxIncline`, `minWidth` e `avoidStairs` — que vão diretamente para o JSON validado por Pydantic no backend. Cada cidade tem o seu router próprio. | **Must-have** | ✅ |
| **RF-02** | Motor de *routing* dinâmico | O backend (FastAPI + OSMnx) recebe as coordenadas e aplica a heurística matemática (*edge weights*) calculando o caminho no grafo com Bellman-Ford em menos de dois segundos. | **Must-have** | ✅ |
| **RF-03** | Interface de mapa "carga cognitiva reduzida" | Sidebar única, mapa Leaflet a ocupar a maioria do *viewport*, controlos progressivos (sliders + dropdown + toggle). | **Must-have** | ✅ |
| **RF-04** | Submissão e re-routing por barreiras temporárias | Endpoint frontend que usa `navigator.geolocation` para intercetar um nó do grafo e marcar `is_blocked = True` temporariamente, desencadeando um recálculo (*crowdsourcing* ativo). | **Must-have** | 🔜 |
| **RF-05** | Feedback sensorial háptico e sonoro | Invocar `navigator.vibrate(200)` e `window.speechSynthesis.speak()` sempre que o utilizador se aproxime de um nó que exija mudança de direção superior a 45 graus. | **Must-have** | 🔜 |
| **RF-06** | Toggle nativo de alto contraste | Floating Action Button global (`z-50`) que atualiza as variáveis nativas do tema CSS, mudando a camada do basemap para `dark_matter` e impondo alto contraste (rácio > 7:1). | **Must-have** | 🔜 |
| **RF-07** | Parsing à prova de falha (sanitizer) | O backend não pode devolver 500 se `width` ou `incline` chegarem mal formatados (ex.: string "narrow") do OpenStreetMap. Cai num *default* seguro. | **Must-have** | ✅ |
| **RF-08** | Navegação GPS turn-by-turn em tempo real | Acompanhar as coordenadas do utilizador com `watchPosition` para mover um marcador e rodar o mapa pelo compasso do dispositivo. | **Nice-to-have** | 🔜 |
| **RF-09** | Botão SOS | Botão rápido embebido no PWA para marcar 112 ou um contacto pré-definido quando a cadeira de rodas encrava ou existe uma urgência. | **Nice-to-have** | 🔜 |
| **RF-10** | Pré-cache do mapa em memória | O servidor processa o ficheiro GraphML no arranque (`startup_event`), carregando o raio de 1,5 km para RAM, evitando picos de memória e esperas longas em cada pedido. | **Must-have** | ✅ |
| **RF-11** | Suporte multi-cidade | Dropdown na sidebar permite alternar entre cidades suportadas (Vila Real e Paris) sem recarregar a página. O backend mantém um router por cidade, pré-aquecido no arranque. | **Must-have** (extensão) | ✅ |
| **RF-12** | Enriquecimento real de elevação | A tag OSM `incline` é esparsa em Vila Real; o backend consulta o conjunto OpenTopoData EU-DEM 25 m no arranque, deriva o declive real por aresta e cacheia em disco. | **Must-have** (extensão) | ✅ |
| **RF-13** | *Snap-point* pedonal | O clique no mapa é projetado sobre a aresta pedonal mais próxima (até 250 m). Vias automóveis (motorway, trunk) são excluídas do alvo de *snap*. | **Must-have** (extensão) | ✅ |

### Critérios de decisão MVP
*   **Must-have:** componentes estruturais e lógica diferenciadora essenciais para a prova de conceito perante o júri / docentes. Sem isto, o projeto não é o CityFlow.
*   **Nice-to-have:** melhorias de qualidade de vida que demandam *overhead* técnico que não traz benefício para a apresentação do conceito.

### Notas sobre o estado entregue
*   Os requisitos marcados como 🔜 — *crowdsourcing*, TTS / vibração, alto contraste, GPS *live*, SOS — estão preservados no *roadmap* porque foram desenhados nas fases iniciais da UC. A defesa do MVP foca-se nos requisitos ✅ (núcleo do motor matemático, *snap-point* pedonal, *routing* multi-cidade e enriquecimento de elevação).
*   Em alternativa ao *toggle* de alto contraste (RF-06), o tema base já cumpre WCAG AA (ver `Requisitos_Acessibilidade_WCAG.md`).
