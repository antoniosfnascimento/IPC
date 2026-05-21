# Tabela de Requisitos Funcionais (CityFlow MVP)

Esta tabela sintetiza a documentação arquitetural do CityFlow num formato de *Product Backlog* focado no Mínimo Produto Viável (MVP), priorizando o núcleo de acessibilidade técnica face às abstrações de negócio.

| ID | Funcionalidade | Descrição técnica (implementação) | Prioridade (MVP) |
| :---: | :--- | :--- | :---: |
| **RF-01** | Seleção de perfil de acessibilidade | O frontend mantém um estado de perfil (via Context API) para alternar entre "Cadeira de Rodas", "Sénior", "Daltónico". Cada perfil emite um JSON estrito, validado por Pydantic no backend. | **Must-have** |
| **RF-02** | Motor de *routing* dinâmico | O backend (FastAPI + OSMnx) recebe as coordenadas e aplica a heurística matemática (*edge weights*) calculando o caminho no grafo com Bellman-Ford em menos de dois segundos. | **Must-have** |
| **RF-03** | Interface de mapa "carga cognitiva reduzida" | Usar Leaflet / react-leaflet com renderização condicional para ocultar a camada base das ruas, deixando visível apenas a *polyline* da rota calculada (modo *Easy Read*). | **Must-have** |
| **RF-04** | Submissão e re-routing por barreiras temporárias | Endpoint frontend que usa `navigator.geolocation` para intercetar um nó do grafo e marcar `is_blocked = True` temporariamente, desencadeando um recálculo (*crowdsourcing* ativo). | **Must-have** |
| **RF-05** | Feedback sensorial háptico e sonoro | Invocar `navigator.vibrate(200)` e `window.speechSynthesis.speak()` sempre que o utilizador se aproxime de um nó que exija mudança de direção superior a 45 graus. | **Must-have** |
| **RF-06** | Toggle nativo de alto contraste | Floating Action Button global (`z-50`) que atualiza as variáveis nativas do tema CSS, mudando a camada do basemap para `dark_matter` e impondo alto contraste (rácio > 7:1). | **Must-have** |
| **RF-07** | Parsing à prova de falha (sanitizer) | O backend não pode devolver 500 se `width` ou `incline` chegarem mal formatados (ex.: string "narrow") do OpenStreetMap. Tem de cair num default seguro. | **Must-have** |
| **RF-08** | Navegação GPS turn-by-turn em tempo real | Acompanhar as coordenadas do utilizador com `watchPosition` para mover um marcador e rodar o mapa pelo compasso do dispositivo. | **Nice-to-have** |
| **RF-09** | Botão SOS | Botão rápido embebido no PWA para marcar 112 ou um contacto pré-definido quando a cadeira de rodas encrava ou existe uma urgência. | **Nice-to-have** |
| **RF-10** | Pré-cache do mapa em memória | O servidor processa o ficheiro GraphML no arranque (`startup_event`), carregando o raio de 1,5 km para RAM, evitando picos de memória e esperas longas em cada pedido. | **Must-have** |

### Critérios de decisão MVP
*   **Must-have:** Componentes estruturais e lógica diferenciadora essenciais para a prova de conceito face ao júri / docentes. Sem isto, o projeto não é o CityFlow.
*   **Nice-to-have:** Melhorias de qualidade de vida excelentes para PWA / mobile que, por outro lado, exigem overhead técnico significativo (live GPS tracking exige filtragem de erro altimétrico, logo não é vital para o protótipo conceptual em que a *rota gerada no ecrã* já prova o conceito).
