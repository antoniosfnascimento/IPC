# Especificação de Desenvolvimento de Software (CityFlow Inclusivo)

**Versão:** 1.3 (*routing* multi-cidade — Vila Real + Paris)
**Fase:** Mínimo Produto Viável (MVP)
**Público-alvo:** Equipas de Engenharia de Software (backend / frontend)

Este documento define a arquitetura técnica, modelos de dados, diagramas UML, contratos de API e lógica algorítmica necessários para implementar o MVP do CityFlow Inclusivo. O motor passou a suportar mais do que uma cidade em simultâneo — ver `Multi_City_Viability_Report.md` para a justificação por dados da escolha das cidades suportadas.

## Histórico de versões

| Versão | Conteúdo |
| :--- | :--- |
| **1.0** | Esqueleto inicial — motor de rotas com pesos customizados em Vila Real, sanitizer defensivo. |
| **1.1** | Interface React + Leaflet com sliders e *toggle*, integração com o motor. |
| **1.2** | Enriquecimento real de elevação via OpenTopoData EU-DEM 25 m. *Snap-point* pedonal com filtragem por tipo de via (raio 250 m). Documentação retraduzida para PT-PT. |
| **1.3** *(atual)* | *Routing* multi-cidade (Vila Real + Paris) com endpoint `GET /api/v1/cities`, dropdown estilizado no frontend, cache persistente de elevação em disco e correção de *stale closure* no handler de cliques do mapa. Scripts de arranque robustos para Windows (.bat + .ps1) e macOS (.sh) com instalação automática de dependências. |

---

## 1. Arquitetura do sistema

Uma arquitetura cliente-servidor padrão com motor geoespacial em memória (*RAM-based graph processing*).

### Stack tecnológico
*   **Frontend (PWA):** React (Vite) integrado com Leaflet.js (renderização de mapas).
*   **Backend (servidor API):** Python 3.10+ via FastAPI (ASGI assíncrono).
*   **Motor de *routing*:** OSMnx, NetworkX e GeoPandas.
*   **Enriquecimento de elevação:** OpenTopoData (gratuito, sem chave, conjunto EU-DEM 25 m).
*   **Armazenamento de grafos:** *MultiDiGraph* persistido em disco em formato GraphML para cache.

### Fluxo de componentes
```mermaid
graph TD
    Client[Cliente Mobile / Web: React + Leaflet] -->|REST API - JSON| API[Servidor FastAPI: main.py]
    API -->|Modelos Pydantic| Validator[Camada de validação: models.py]
    Validator -->|Objetos Python| Engine[Motor de grafos: router.py]
    Engine -->|I/O| Disk[(Cache local OSM: GraphML)]
    Engine -->|HTTP| Elev[(OpenTopoData EU-DEM)]
    Engine -->|Sub-rotinas| Alg[Bellman-Ford com peso customizado]
```

---

## 2. Modelação de dados

O estado é mantido na rede viária do OSM e nos parâmetros de sessão submetidos pelo cliente, mais *blocked edges* para suportar a funcionalidade de *crowdsourcing* (planeada).

### Diagrama de classes (motor backend)
```mermaid
classDiagram
    class UserProfile {
        +UUID id
        +String profile_name
        +Float max_incline
        +Float min_width
        +Boolean avoid_stairs
        +List~String~ surface_preference
        +validate() Boolean
    }

    class CityConfig {
        +String slug
        +String display_name
        +Tuple~Float, Float~ center
        +Integer radius_meters
    }

    class MapEngine {
        -MultiDiGraph G
        -Tuple~Float, Float~ center_point
        -Integer config_radius_mts
        -String cache_key
        -List~Tuple~ blocked_edges
        +load_graph()
        +annotate_graph_with_elevation()
        +report_barrier(Tuple coords) Boolean
        +get_route(Tuple start, Tuple end, UserProfile profile) List~Tuple~
        +snap_point(Tuple coords) Dict
    }

    class EdgeData {
        +Integer node_u
        +Integer node_v
        +String highway_type
        +Float length_mts
        +Float incline_pct
        +Float grade_abs
        +Float width_mts
        +String surface_type
        +Float custom_weight
        +Boolean is_blocked
        +calculate_penalty(UserProfile profile) Float
    }

    class FeatureSanitizer {
        <<Utility>>
        +parse_float(value, Float default) Float
        +sanitize_width(value) Float
        +normalize_surface(String raw_surface) String
    }

    MapEngine "1" *-- "many" EdgeData
    MapEngine ..> UserProfile
    MapEngine ..> FeatureSanitizer
    MapEngine ..> CityConfig
```

### Atributos das arestas (dicionário de dados)
Cada aresta em memória carrega as tags OSM mais os campos derivados da elevação:
*   `osmid` (list/int): identificador único do OSM.
*   `highway` (string): classificação da via (`footway`, `steps`, `residential`).
*   `length` (float): comprimento em metros.
*   `incline` (string → float): declive original do OSM ("5%", "-2%", "up").
*   `grade_abs` (float): declive por aresta calculado de `(elev_v − elev_u) / comprimento`, limitado a 0,25 e suavizado em arestas curtas.
*   `surface` (string): tipo de piso.
*   `is_blocked` (boolean, planeado): flag dinâmica colocada quando um utilizador reporta um obstáculo.

---

## 3. Contratos da API

JSON sobre HTTP. O sistema é *stateless* entre chamadas.

### 3.1. `POST /api/v1/route`
**Objetivo:** devolver as coordenadas de uma rota sob as restrições do utilizador.

**Corpo do pedido:**
```json
{
  "start_coords": [41.2954, -7.7451],
  "end_coords": [41.2982, -7.7420],
  "city": "vila_real",
  "profile": {
    "profile_name": "wheelchair",
    "max_incline": 0.08,
    "min_width": 1.2,
    "avoid_stairs": true,
    "surface_preference": ["paved", "asphalt", "concrete"]
  }
}
```

O campo `city` é opcional e por defeito é `vila_real`. Valores permitidos: `vila_real`, `paris`. A lista completa também é exposta por `GET /api/v1/cities`.

**Resposta (200 OK):**
```json
{
  "status": "success",
  "city": "vila_real",
  "route_geometry": [[41.2954, -7.7451], [41.2956, -7.7450]],
  "distance_meters": 1250.5,
  "max_route_incline": 0.071
}
```

Códigos de erro:
*   **424 Failed Dependency:** as restrições não permitem nenhuma rota viável (típico de perfis ultra-restritivos entre dois pontos separados por uma única encosta íngreme).

### 3.2. `POST /api/v1/snap-point`
**Objetivo:** projetar uma coordenada de clique sobre a rua pedonal mais próxima, até 250 m.

**Corpo do pedido:**
```json
{ "coords": [41.2960, -7.7445], "city": "vila_real" }
```

`city` é opcional e por defeito é `vila_real`.

**Resposta (200 OK):**
```json
{
  "status": "success",
  "city": "vila_real",
  "snapped_coords": [41.29603, -7.74428],
  "distance_meters": 12.4,
  "adjusted": true
}
```

Códigos de erro:
*   **422 Unprocessable Entity:** o ponto está a mais de 250 m de qualquer aresta pedonal. A mensagem da API inclui a distância para o utilizador perceber a margem.

### 3.3. `GET /api/v1/cities`
**Objetivo:** *endpoint* de descoberta usado pelo *dropdown* do frontend.

**Resposta:**
```json
{
  "default": "vila_real",
  "cities": [
    { "slug": "vila_real", "display_name": "Vila Real", "center": [41.296, -7.746], "radius_meters": 1500 },
    { "slug": "paris",     "display_name": "Paris",     "center": [48.8584, 2.347], "radius_meters": 1500 }
  ]
}
```

### 3.4. `POST /api/v1/report-barrier` (planeado)
**Objetivo:** *endpoint* de *crowdsourcing*. O backend encontra a aresta mais próxima das coordenadas e marca `is_blocked = True`, forçando recálculo.

---

## 4. Motor de pesos

A função custo do Bellman-Ford multiplica o comprimento de cada aresta pelas penalizações de acessibilidade:

$$W_e = \text{comprimento}_e \times \prod_{i=1}^{n} \text{penalização}_i$$

**Lógica condicional (versão entregue, simplificada):**
```python
penalty_total = 1.0

# Crowdsourcing (planeado)
if data['is_blocked']:
    penalty_total = 99999.0

# Escadas como barreira (cadeira de rodas / carrinho de bebé)
if data['highway'] == 'steps' and profile.avoid_stairs:
    penalty_total *= 10000.0

# Superfície fora das preferidas
if data['surface'] not in profile.surface_preference:
    penalty_total *= 3.5

# Declive (preferimos o gradiente real à tag OSM `incline`)
grade = data['grade_abs'] or osm_incline_fallback(data['incline'])
if grade > profile.max_incline:
    penalty_total *= 15.0
elif grade > profile.max_incline * 0.75:
    penalty_total *= 3.0      # tier suave de aproximação ao limite

# Largura (com fallback defensivo a 0,5 m)
if data['width'] < profile.min_width:
    penalty_total *= 5.0

W_e = data['length'] * penalty_total
```

---

## 5. Estado e UI no frontend

### State machine de navegação inclusiva (MVP entregue)
```mermaid
stateDiagram-v2
    [*] --> CityChosen: arranque carrega /cities
    CityChosen --> SelectingPoints: clica no mapa
    SelectingPoints --> FormReady: A e B definidos
    FormReady --> CalculatingRoute: pressiona "Calcular"
    CalculatingRoute --> RouteDisplayed: 200 OK
    CalculatingRoute --> Errored: 424 / network
    Errored --> SelectingPoints: utilizador reage
    RouteDisplayed --> SelectingPoints: 3.º clique limpa
    CityChosen --> CityChosen: troca de cidade
```

### Funcionalidades MVP de UI (entregue)
1.  **Sidebar única e fixa:** *single source of truth* — cidade, perfil, estado da rota e alertas vivem na mesma coluna. Em mobile, transforma-se em *drawer* lateral.
2.  **Dropdown estilizado de cidade:** componente custom com chip, *chevron* animado, *listbox* acessível por teclado (`Enter`/`Space`/`Esc`), fecha-se com clique fora.
3.  **Sliders e *toggle*:** controlos diretos sobre `max_incline`, `min_width` e `avoid_stairs`. O efeito é visível na próxima rota calculada.
4.  **Toasts dentro da sidebar:** informativo (azul) ou de alerta (vermelho), com `role="status"`/`role="alert"` para leitores de ecrã.
5.  **Painel de métricas:** distância, tempo estimado (ajustado ao perfil), inclinação crítica com *badge* verde/vermelho.

### Funcionalidades planeadas
1.  **Modo *Easy Read*:** renderização condicional para esconder o tile base e mostrar apenas a *polyline* e ícones W3C de curva.
2.  **Web Speech API / Vibration API:** TTS e feedback háptico nas manobras.
3.  **Botão "Reportar obstáculo":** ≥ 44×44 px, fixo no rodapé, integrado com `report-barrier`.
4.  **Toggle de alto contraste:** muda basemap para CartoDB Dark Matter e força contraste ≥ 7:1.
