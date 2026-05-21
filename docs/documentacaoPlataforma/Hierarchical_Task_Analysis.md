# Análise Hierárquica de Tarefas (HTA) — CityFlow MVP

Este documento aplica a metodologia *Hierarchical Task Analysis* à principal jornada de valor do CityFlow. O objetivo é identificar cada ponto de fricção onde o frontend ou o backend podem falhar perante o utilizador, definindo o tratamento de erro correspondente.

## Tarefa principal (Macro-Task) — Nível 0
**0. Planear uma rota inclusiva e segura** (objetivo: ir de A para B sem cruzar barreiras físicas intoleráveis).

| HTA | Sub-tarefa | Ação do utilizador (frontend) | Processo do sistema (backend / app) | Condição de erro e tratamento |
| :---: | :--- | :--- | :--- | :--- |
| **1.** | **Definir perfil base** | Clica num *card* ou *toggler* ("Cadeira de rodas / visual / sénior"). | Carrega as constantes (restrições) para o estado global da aplicação (ex.: `max_incline: 0.08`). | **Erro (1.1):** o utilizador não escolhe perfil.<br>**Tratamento:** o botão de submissão fica *disabled* e um alerta visual pede um perfil. |
| **2.** | **Inserir coordenadas de origem** | Escreve no campo "origem" ou clica no botão GPS "a minha localização". | O sistema adquire e sanitiza a string via *geocoder* (Nominatim) ou `navigator.geolocation`. O Pydantic converte para `[lat, lon]`. | **Erro (2.1):** o browser nega permissões de GPS.<br>**Tratamento:** fallback para entrada manual com mensagem amigável: "introduz a origem por texto". A app não pode crashar. |
| **3.** | **Inserir destino** | Escreve no campo "destino" ou toca no mapa Leaflet. | Traduz o texto numa coordenada geográfica precisa. | **Erro (3.1):** destino fora da malha em RAM pré-carregada para a cidade ativa (raio > 1,5 km).<br>**Tratamento:** o FastAPI responde com 400. O frontend diz: "destino fora da área metropolitana atualmente mapeada". |
| **4.** | **Submeter (início do request à API)** | Aciona o botão "Calcular" (alvo 44×44 px — WCAG 2.5.5). | O frontend envia o POST model preenchido para o backend, incluindo o slug da cidade ativa. | **Erro (4.1):** falha de Internet do lado do cliente.<br>**Tratamento:** *toast* "ligação à rede perdida" que para o *spinner* de carregamento. |
| **5.** | **Calcular variáveis do grafo** | Espera analítica (*spinner*). | O motor Python de *routing* executa o Bellman-Ford sobre o `NetworkX`, ponderando as arestas do grafo da cidade selecionada. | **Erro (5.1):** tags OSM corrompidas partem a matemática.<br>**Tratamento:** o `FeatureSanitizer.parse_float()` força defaults seguros. Erro silenciado perante o utilizador. |
| **6.** | **Validar barreiras (edge case)** | Transparente / imediato (durante o passo 5). | O Bellman-Ford tenta ligar origem (nó U) e destino (nó V) através de arestas de peso finito. O destino está fisicamente "rodeado por escadas". | **Erro (6.1):** beco-sem-saída isolado (sem solução abaixo do tecto).<br>**Tratamento:** o FastAPI responde com 424 Failed Dependency. O cliente diz: "destino fisicamente impossível ou isolado por este perfil." |
| **7.** | **Renderização sensorial de sucesso** | O utilizador observa a rota renderizada. | O Leaflet desenha a *polyline* grossa preenchida. A app anuncia "início da viagem" por TTS. | **Erro (7.1):** a rota sobrepõe-se a ruas não pedonais e confunde a base do Leaflet.<br>**Tratamento:** camadas Leaflet corretamente indexadas (z-index) para que a *polyline* fique sempre opaca por cima. |

*Nota metodológica:* se o passo 6 não falhar, a macro-tarefa 0 considera-se concluída com sucesso (o utilizador pode iniciar a viagem física).
