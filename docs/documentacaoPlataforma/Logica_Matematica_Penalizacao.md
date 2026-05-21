# Heurísticas de Penalização e Lógica Matemática (Motor de *Routing*)

Este documento especifica os pesos numéricos exatos que o algoritmo de *routing* atribui às arestas (ruas) do grafo para evitar intencionalmente caminhos não acessíveis, calculando o *custo efetivo* de cada via.

A fórmula central do motor de pesos é:
`Custo direcional (W) = Distância física (m) × Σ penalizações`

---

## 1. Tabela de penalização por superfície

Baseada no atributo OSM `surface`. Valores > 1,0 representam esforço / desconforto adicional para cadeiras de rodas e andarilhos.

| Tipo de superfície (tag OSM) | Descrição | Penalty point | Lógica |
| :--- | :--- | :--- | :--- |
| `paved`, `asphalt`, `concrete` | Pavimento liso consolidado | **1,0 (neutro)** | Piso ideal. Sem atrito adicional. Uma rua de 100 m "custa" 100 m. |
| `paving_stones`, `sett` | Calçada consolidada (pedra) | **1,5** | Aumenta o custo em 50 %. Alguma vibração e esforço de impulso, mas perfeitamente transitável e inerente a centros históricos como Vila Real. |
| `cobblestone` | Calçada portuguesa (irregular) | **3,5** | Elevada trepidação, risco de prender rodas dianteiras e muletas escorregarem (em piso molhado). Uma via de 100 m passa a custar 350 m, empurrando o algoritmo para um desvio mais longo em asfalto. |
| `compacted`, `fine_gravel` | Terra batida / gravilha fina | **5,0** | Muito esforço de tração. As rodas afundam ligeiramente. Evitar a quase todo o custo. |
| `gravel`, `dirt`, `sand` | Gravilha solta, terra, areia | **20,0** | Praticamente intransitável para auxílios de mobilidade. Atua quase como uma barreira. |

---

## 2. Penalizações por barreiras e variáveis estáticas

Aplicadas transversalmente sempre que existem obstáculos explícitos na via.

| Tipo de barreira (OSM / API) | Perfil afetado | Penalty point | Lógica |
| :--- | :--- | :--- | :--- |
| `highway=steps` (escadas) | Cadeira de rodas, carrinho de bebé | **10000,0 (infinito / corte)** | Barreira arquitetónica intransponível (*hard constraint*). O peso torna impossível ao algoritmo escolher este caminho, independentemente da distância alternativa. |
| Passadeira sem sinal sonoro | Invisual / baixa visão | **10,0** | Risco severo. Empurra invisuais para interseções sinalizadas ou para passeios contínuos protegidos — aceitam-se rotas dez vezes mais longas em troca de segurança. |
| `is_blocked=True` (*crowdsourcing*) | Todos | **99999,0 (corte temporal)** | Feedback submetido por utilizadores (obras, carro estacionado no passeio). Corta temporariamente a aresta. |

---

## 3. A matemática por trás do multiplicador 15,0 do declive

A justificação teórica em engenharia civil e biomecânica para a constante `15.0` na função de penalização do declive baseia-se na *lei do trabalho excessivo* e no esgotamento da força humana de propulsão em planos inclinados.

### Porquê não `2.0` ou `5.0`? (Estudo do coeficiente)
Se definíssemos que uma rua acima do limite da cadeira de rodas (ex.: > 8 %) tivesse uma penalização leve (ex.: `2.0`), o algoritmo leria uma subida íngreme de 100 m como um percurso de "200 m".
*   **O problema com um peso baixo:** se a alternativa (a rua plana ideal) exigir um desvio de 300 m, o algoritmo continuaria a escolher a rua íngreme (200 de custo vs 300). Isso **obrigaria o utilizador a subir uma colina que não consegue manter à mão**, comprometendo a sua saúde ou causando uma queda da cadeira de rodas para trás — risco fatal.

### A função exponencial de esforço
Na locomoção humana assistida, a energia necessária para vencer a gravidade num plano inclinado superior a 5 % segue uma curva assintótica. A fadiga muscular dos braços cresce exponencialmente.
*   Uma subida de 8 % é tolerável apenas em distâncias muito curtas.
*   Uma rampa de 12 % sem corrimão é frequentemente intransponível independentemente da distância.

**Ao definirmos Penalização = 15.0**, dizemos ao grafo: *"subir esta colina de 100 m custa-te o equivalente a uma viagem plana de 1,5 km".*

Esse custo elevado obriga o Bellman-Ford a "entrar em pânico" e procurar dezenas de alternativas, preferindo enviar o utilizador num ziguezague de 1,2 km por avenidas planas em vez de o atirar contra uma subida direta para a UTAD. Este coeficiente foi testado como a *golden ratio* para micro-routing — alto o suficiente para desviar, baixo o suficiente para manter o grafo conectado.

---

## 4. Enriquecimento real de elevação (substitui tags OSM `incline` esparsas)

A `incline` do OSM cobre menos de 5 % das ruas em Vila Real. Sem uma fonte real de declive, qualquer filtro degenera para 0 %.

No arranque, o motor consulta o **OpenTopoData** (gratuito, sem chave de API, conjunto EU-DEM a 25 m de resolução) para cada nó do grafo e guarda a elevação. Cada aresta calcula o seu declive como `(elev_v − elev_u) / comprimento`.

São aplicadas duas correções:
1. **Limite a 25 %.** O DEM tem resolução de 25 m; diferenças em arestas muito curtas (< 20 m) tendem a ser ruidosas. O declive é limitado a [-0,25, 0,25].
2. **Suavização em arestas curtas.** Quando uma aresta é mais curta do que a resolução do DEM, o declive é multiplicado por `comprimento / 20`, reduzindo o ruído de uma única amostra de elevação.

O router prefere o declive derivado da elevação e só recorre à tag OSM `incline` quando o enriquecimento de elevação falha.
