# Análise Hierárquica de Tarefas (HTA) — CityFlow MVP

Este documento aplica a metodologia *Hierarchical Task Analysis* à principal jornada de valor do CityFlow. O objetivo é identificar cada ponto de fricção onde o frontend ou o backend podem falhar perante o utilizador, definindo o tratamento de erro correspondente.

A coluna **Estado** indica se o sub-passo está implementado no MVP entregue (✅) ou no *roadmap* (🔜).

## Tarefa principal (Macro-Task) — Nível 0
**0. Planear uma rota inclusiva e segura** (objetivo: ir de A para B sem cruzar barreiras físicas intoleráveis).

| HTA | Sub-tarefa | Ação do utilizador (frontend) | Processo do sistema (backend / app) | Condição de erro e tratamento | Estado |
| :---: | :--- | :--- | :--- | :--- | :---: |
| **1.** | **Escolher a cidade ativa** | Abre o *dropdown* "Cidade" e seleciona Vila Real ou Paris. | O frontend lê `/api/v1/cities`. Ao trocar, o mapa voa para o novo centro, o estado é limpo e os pedidos seguintes incluem o slug da cidade. | **Erro (1.1):** o endpoint `/cities` falha.<br>**Tratamento:** fallback estático com Vila Real + Paris hardcoded na app. | ✅ |
| **2.** | **Definir o perfil de acessibilidade** | Ajusta os sliders de inclinação máxima (2 %–15 %) e largura mínima (0,5 m–2,0 m); ativa ou desativa o *toggle* "Evitar escadas". | O frontend mantém os três valores em estado React; só são enviados ao backend no momento do cálculo. | **Erro (2.1):** valores fora do *range* (impossível no MVP, pois os sliders são limitados na UI). | ✅ |
| **3.** | **Definir partida** | Clica no mapa, dentro do raio de cobertura. | O frontend envia `POST /api/v1/snap-point` com a cidade ativa. O backend projeta para a aresta pedonal mais próxima (até 250 m). | **Erro (3.1):** clique a mais de 250 m de qualquer rua pedonal.<br>**Tratamento:** API responde 422; sidebar mostra "Esse ponto está a X m de uma rua pedonal…". | ✅ |
| **4.** | **Definir destino** | Segundo clique no mapa. | Igual ao passo 3. | Mesmo tratamento de erro. | ✅ |
| **5.** | **Submeter o pedido de rota** | Pressiona "Calcular rota segura". | O frontend envia `POST /api/v1/route` com coordenadas, cidade e perfil. O backend recalcula os pesos para todas as arestas e corre Bellman-Ford. | **Erro (5.1):** falha de rede ou timeout (>12 s).<br>**Tratamento:** axios.timeout dispara mensagem amigável e desativa o spinner. | ✅ |
| **6.** | **Validar viabilidade da rota** | Espera analítica (*spinner*). | O motor avalia se origem e destino estão na malha (≤ 500 m do nó mais próximo) e se existe caminho com peso finito. | **Erro (6.1):** sem rota viável (*deadlock* de restrições).<br>**Tratamento:** API devolve 424; a sidebar mostra "Não existe rota possível com as restrições atuais (inclinação máx.: X %, largura mín.: Y m)." | ✅ |
| **7.** | **Renderizar a rota** | O utilizador observa a *polyline* azul no mapa e o painel de métricas (distância, tempo, inclinação crítica). | O Leaflet desenha a *polyline* e os marcadores; o painel calcula o tempo via velocidade adaptada ao perfil. | **Erro (7.1):** a rota sobrepõe-se à camada de ruas e fica difícil de ler.<br>**Tratamento:** `weight: 6` e `opacity: 0.8` garantem visibilidade; o azul é distinto dos tons do basemap. | ✅ |
| **8.** | **Interpretar resultado** | O utilizador lê o *badge* verde/vermelho (dentro/fora do limite de conforto). | Comparação `max_route_incline > maxIncline` no frontend. | N/A — leitura passiva. | ✅ |
| **9.** | **Reportar obstáculo dinâmico** | Pressiona "Reportar caminho cortado". | O frontend envia `POST /api/v1/report-barrier` com a localização; o backend marca `is_blocked=True` na aresta. | A rota recalcula automaticamente. | 🔜 |
| **10.** | **Receber instruções turn-by-turn** | Caminha fisicamente; o telemóvel vibra e o TTS anuncia manobras. | `navigator.geolocation.watchPosition` + Web Speech + Vibration API. | Em zonas sem GPS, o sistema avisa e mantém a vista estática. | 🔜 |

*Nota metodológica:* se o passo 6 não falhar, a macro-tarefa considera-se concluída para efeitos do MVP (o utilizador tem a rota desenhada e as métricas — pode iniciar a viagem física, embora a navegação ativa, passos 9 e 10, não esteja na versão entregue).
