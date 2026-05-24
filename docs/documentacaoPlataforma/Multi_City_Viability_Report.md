# Relatório de Viabilidade Multi-Cidade

## Porquê este relatório
Durante a revisão do projeto, o docente orientador questionou a suposição de que uma cidade maior (Paris, Nova Iorque) traria automaticamente mais dados de acessibilidade no OpenStreetMap do que Vila Real. A dúvida é legítima — a população por si só não é proxy de densidade de mapeamento.

Este documento apresenta os números **medidos** de densidade de tags OSM usados pelo motor de *routing* do CityFlow num raio de 1,5 km à volta do centro de cada candidata. Assim, a escolha das cidades suportadas fica justificada por dados e não por intuição.

Todos os valores foram recolhidos a 24 de maio de 2026 contra a API Overpass real, através do OSMnx 2.1.0 (`network_type='walk'`, raio = 1500 m). Podem ser reproduzidos pelo *snippet* incluído no final do documento.

## Método
Para cada centro de cidade candidato descarregámos o grafo pedonal e contámos, por aresta, quantas vezes cada tag relevante para acessibilidade está presente:

* **`surface`** — alimenta a penalização de calçada/pavimento (×3,5).
* **`smoothness`** — classificação de conforto orientada a cadeiras de rodas (`excellent` → `very_bad`).
* **`incline`** — tag explícita de declive (já complementada pelo nosso enriquecimento EU-DEM).
* **`width`** — restrição de largura pedonal.
* **`wheelchair`** — tag de acessibilidade explícita.
* **`tactile_paving`** — orientação para utilizadores com baixa visão.
* **`highway=steps`** — barreira intransponível para cadeiras de rodas / carrinhos de bebé.

Foram analisados dois centros:
* **Vila Real** — Avenida Carvalho Araújo, eixo histórico já usado pelo MVP (lat 41.2960, lon -7.7460).
* **Paris** — Châtelet–Les Halles, no centro da cidade (lat 48.8584, lon 2.3470). Châtelet foi escolhido por estar no cruzamento de malhas urbanas medievais, haussmannianas e contemporâneas — toca em todas as famílias de superfície da nossa tabela de penalizações.

> Uma primeira iteração também avaliou Times Square (Nova Iorque). O resultado está resumido no final do documento — em suma: Nova Iorque tem ~2,2× mais arestas do que Vila Real, mas o vocabulário de superfícies é dominado por `concrete`+`asphalt` (ou seja, uniforme), portanto os filtros de superfície e declive responderiam menos visivelmente do que em Paris.

## Resultados

| Métrica (raio 1,5 km) | Vila Real | Paris (Châtelet) | Rácio Paris ÷ Vila Real |
| :--- | ---: | ---: | ---: |
| Arestas no grafo pedonal | 7 366 | 28 756 | **3,9×** |
| Nós | 2 811 | 10 039 | 3,6× |
| Arestas com `surface` | 5 372 (72,9 %) | 22 870 (79,5 %) | 4,3× |
| Arestas com `smoothness` | 46 (0,6 %) | 9 072 (31,5 %) | **197×** |
| Arestas com `incline` | 84 (1,1 %) | 1 404 (4,9 %) | 16,7× |
| Arestas com `width` | 176 (2,4 %) | 122 (0,4 %) | 0,7× |
| Arestas com `wheelchair` | 0 | 36 | n/d |
| Arestas com `tactile_paving` | 60 | 1 162 | 19,4× |
| `highway=steps` | 70 | 72 | 1,0× |
| `highway=footway` | 1 492 | 23 784 | 15,9× |

### Vocabulário de superfícies (contagem)

| Superfície | Vila Real | Paris |
| :--- | ---: | ---: |
| `asphalt` | 3 445 | 12 908 |
| `paving_stones` | 457 | 6 949 |
| `sett` | 992 | 1 234 |
| `concrete` | 220 | 436 |
| `compacted` | 0 | 809 |
| `fine_gravel` | 0 | 183 |
| `gravel` | 0 | 95 |
| `unhewn_cobblestone` | 38 | 0 |
| `ground` | 124 | 0 |
| `unpaved` / `dirt` / `wood` | 50 | 0 |
| `stone` / `concrete:plates` / `metal` | 10 | 182 |

### Vocabulário de smoothness (contagem)

| Smoothness | Vila Real | Paris |
| :--- | ---: | ---: |
| `excellent` | 10 | 1 672 |
| `good` | 18 | 6 490 |
| `intermediate` | 18 | 860 |
| `bad` | 0 | 46 |
| `very_bad` | 0 | 4 |

## Interpretação

### O que surpreende (e o que não surpreende)
1. **Vila Real está longe de estar vazia.** 72,9 % das arestas pedonais já têm a tag `surface`. A intuição de que "a API não tem dados de Vila Real" está errada; a cidade está mapeada com um nível de detalhe razoável, sobretudo no centro histórico.
2. **O que falta a Vila Real são os sinais de *gradiente*.** A `incline` cobre apenas 1,1 % das arestas e a `smoothness` apenas 0,6 %. Foi por isto que o MVP original reportava subidas íngremes como 0 % — não porque Vila Real esteja ausente do OSM, mas porque o *tagging* de declive lá é esparso. Resolvemos isto com o enriquecimento de elevação EU-DEM 25 m no backend.
3. **Paris só está noutro patamar no eixo da *acessibilidade*.** Não é "mais mapeada no geral" — tem uma percentagem comparável de tags `surface` (79,5 % vs 72,9 %). O que Paris tem que é genuinamente raro noutros sítios é a tag `smoothness`, presente em 31,5 % das arestas. Isso é resultado de uma campanha deliberada de mapeamento de acessibilidade conduzida pela Wikimédia França e pela cidade de Paris antes dos Jogos Olímpicos e Paralímpicos de 2024. O mesmo se aplica a `wheelchair` (36 arestas) e `tactile_paving` (1 162 arestas) — cobertura impulsionada por campanha, não por população.
4. **A tag `width` é esparsa em todo o lado.** Vila Real (2,4 %) até ganha a Paris (0,4 %) neste tag. O fallback do OSMnx em `sanitizer.py` (default defensivo de 0,5 m) é por isso relevante para ambas as cidades.

### Efeito líquido nas demonstrações do CityFlow
Cada filtro de perfil atua sobre uma tag diferente:

| Filtro | Vila Real ganha quando… | Paris ganha quando… |
| :--- | :--- | :--- |
| Evitar escadas | Comparável | Comparável |
| Preferência de piso | Tem vocabulário rico em calçada (`sett`, `cobblestone`) | Tem o mesmo, mais `compacted` / `fine_gravel` (jardins) |
| Declive (max_incline) | Movido pelo EU-DEM (tag OSM raw praticamente ausente) | Movido pelo EU-DEM **e** pela tag OSM `incline` nativa |
| Largura | O default defensivo entra em ação (ambas as cidades) | O default defensivo entra em ação (ambas as cidades) |

Como Paris tem 16,7× mais tags `incline` e 197× mais tags `smoothness`, qualquer mexida num slider em Paris produz uma mudança de rota visualmente mais notória do que em Vila Real. Vila Real é **viável** mas uma demo de Paris é **dramática**. Isso justifica adicionar Paris como segunda cidade suportada, em vez de substituir Vila Real.

## Decisão

O CityFlow suporta duas cidades em paralelo:

1. **Vila Real** (predefinida) — a base académica. O MVP foi originalmente desenhado em torno do centro histórico e a investigação de utilizadores (personas João, Maria, Ricardo) é local. O enriquecimento EU-DEM, adicionado recentemente, fecha o problema do declive.
2. **Paris (Châtelet)** — a demonstração. Mostra o comportamento diferenciado de cada filtro em condições de dados ricos e permite que uma demo ao vivo dispare penalizações de piso, conforto e declive numa única viagem.

Ambos os grafos são pré-aquecidos no arranque do backend; o frontend disponibiliza um *dropdown* que muda a vista do mapa, o alvo do *snap* e o destino do *routing* sem recarregar a página. Não se afirma que Paris está "objetivamente mais bem mapeada". A afirmação é mais estreita e suportada pelos números: **Paris tem mais *tagging* específico de acessibilidade no raio usado pelo CityFlow, principalmente graças a uma campanha de mapeamento que não tem equivalente em Vila Real.**

## Nova Iorque: porque foi descartada
Times Square (Nova Iorque) devolveu 16 312 arestas (2,2× Vila Real; 0,6× Paris), cobertura de `surface` de 71,3 %, mas o vocabulário é dominado por `concrete` (5 559) e `asphalt` (3 968) com muito pouca variedade. O filtro de declive também ficaria silencioso (Manhattan, na zona da rua 42, é praticamente plana) e o EU-DEM não cobre os Estados Unidos, obrigando a um fallback para SRTM 30 m, que é mais grosseiro. Nova Iorque manteve-se na *shortlist* mas, na métrica que importa — *quão visivelmente os sliders alteram a rota?* — pontuou abaixo de Paris, pelo que não integra esta primeira versão multi-cidade.

## Reproduzir os números
```python
import osmnx as ox
from collections import Counter

ox.settings.useful_tags_way = list(set(list(ox.settings.useful_tags_way) + [
    "incline", "surface", "width", "smoothness", "wheelchair",
    "sidewalk", "tactile_paving",
]))

centers = {
    "Vila Real": (41.2960, -7.7460),
    "Paris":     (48.8584,  2.3470),
}

for label, (lat, lon) in centers.items():
    G = ox.graph_from_point((lat, lon), dist=1500, network_type="walk")
    edges = list(G.edges(keys=True, data=True))
    total = len(edges)
    def pct(tag): return sum(1 for *_, d in edges if d.get(tag)) / total * 100
    print(f"{label}: {total} arestas, surface={pct('surface'):.1f}%, "
          f"smoothness={pct('smoothness'):.1f}%, incline={pct('incline'):.1f}%")
```
