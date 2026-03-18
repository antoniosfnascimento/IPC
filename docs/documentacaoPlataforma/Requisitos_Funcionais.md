# Tabela de Requisitos Funcionais (CityFlow MVP)

Esta tabela sintetiza a documentação arquitetural do CityFlow num formato de *Product Backlog* focado no Mínimo Produto Viável (MVP), priorizando o core de acessibilidade técnica perante as abstrações de negócio.

| ID | Funcionalidade | Descrição Técnica (Implementação) | Prioridade (MVP) |
| :---: | :--- | :--- | :---: |
| **RF-01** | Seleção de Perfil de Acessibilidade | O Frontend deve possuir uma State Machine (ex: via Context API) para alternar entre "Cadeira de Rodas", "Idoso", "Daltónico". Cada perfil deve emitir um JSON estrito para o backend validado por Pydantic. | **Must-have** |
| **RF-02** | Motor de Roteamento Dinâmico | O Backend (FastAPI + OSMnx) deve receber as coordenadas e aplicar a heurística matemática (*Edge Weights*) calculando o caminho no Grafo através do algoritmo de Dijkstra com tempos sub-2 segundos. | **Must-have** |
| **RF-03** | Interface de Mapa "Carga Cognitiva Reduzida" | Utilizar o Leaflet/React-Leaflet com possibilidade de aplicar *Conditional Rendering* para ocultar a malha viária de fundo, deixando visível apenas a *Polyline* da rota calculada (Modo Easy Read). | **Must-have** |
| **RF-04** | Submissão e Recálculo por Barreiras Temporárias | Endpoint via `navigator.geolocation` no Front que interceta um nó do grafo e atribui `is_blocked = True` temporário, acionando um trigger de recálculo (Crowdsourcing ativo). | **Must-have** |
| **RF-05** | Feedback Sensorial Háptico e Sonoro | Invocar `navigator.vibrate(200)` e `window.speechSynthesis.speak()` sempre que o utilizador se aproxime das coordenadas de um nó que exija alteração de direção superior a 45 graus. | **Must-have** |
| **RF-06** | Alternância de Alto Contraste Nativo | Botão Global (Floating Action Button fixo em `z-50`) que modifique as variáveis nativas de CSS do Tema Tailwind, alternando o layer geográfico de base para `dark_matter` e injetando alto contraste (rácio >7:1). | **Must-have** |
| **RF-07** | Parsing à Prova de Falha (Sanitizer) | O backend não pode devolver 500 no cálculo de rota se o dado de `width` ou `incline` vier mal codificado (ex: string "narrow") da API livre do OpenStreetMap. Tem de reverter para Default de Segurança. | **Must-have** |
| **RF-08** | Navegação GPS Em Tempo Real (Turn-by-turn) | Monitorizar ativamente a mudança contínua de coordenadas via `watchPosition` para colocar um marcador móvel e rotacionar o mapa de acordo com a bússola do telemóvel nativo. | **Nice-to-have** |
| **RF-09** | Botão SOS/Alarme | Um botão rápido incorporado na framework (PWA) de discagem direta para 112 ou contacto predefinido caso a cadeira de rodas fique encravada ou exista urgência na vida real. | **Nice-to-have** |
| **RF-10** | Pre-Caching do Mapa em Memória | O servidor processa o ficheiro GraphML no arranque (`startup_event`) carregando para a memória RAM os 1.5Km radiais, impedindo picos de RAM e tempos de espera enormes a cada submit. | **Must-have** |

### Critérios de Decisão MVP
*   **Must-have:** Componentes estruturais e lógicas diferenciadoras vitais à prova do conceito perante o júri/professores. Sem isto, o projeto não é o *CityFlow*.
*   **Nice-to-have:** Melhorias incríveis de Qualidade de Vida (QoL) para PWA/Mobile que, em contrapartida, demandam elevado overhead técnico (Navegação GPS em Live-tracking real exata exige filtragem de erro altimétrico, logo não é vital para o protótipo conceptual onde apenas a *rota gerada no ecrã* já prova o ponto).
