# Heurísticas de Penalização e Lógica Matemática (Routing Engine)

Este documento especifica os valores numéricos exatos (pesos) que o algoritmo de *routing* atribui às arestas (ruas) do grafo para evitar intencionalmente caminhos não acessíveis, calculando o "Custo Efetivo" da via.

A fórmula central para o Motor de Pesos é:
`Custo Direcional (W) = Distância Física (m) * Somatório das Penalizações`

---

## 1. Tabela de Penalização por Superfície (Surface Types)

Baseado nos atributos `surface` do OpenStreetMap. Valores > 1.0 indicam aumento de "esforço/desconforto" para cadeiras de rodas e andarilhos.

| Tipo de Superfície (OSM Tag) | Descrição do Piso | Peso (Penalty Point) | Lógica da Atribuição |
| :--- | :--- | :--- | :--- |
| `paved`, `asphalt`, `concrete` | Pavimento Liso Consolidado | **$1.0$ (Neutro)** | Piso ideal. Não existe atrito extra. Uma rua de 100m "custa" 100m. |
| `paving_stones`, `sett` | Calçada (Pedra Consolidada) | **$1.5$** | Aumenta o custo em 50%. Causa alguma vibração e esforço de impulsão, mas é perfeitamente transitável e inerente a centros históricos (ex: Vila Real). |
| `cobblestone` | Calçada Portuguesa (Irregular) | **$3.5$** | Elevada trepidação, risco de prender rodízios dianteiros das cadeiras de rodas e muletas escorregarem (se molhado). Uma via de 100m passa a "custar" o esforço de 350m, forçando o algoritmo a preferir um desvio mais longo se for de asfalto liso. |
| `compacted`, `fine_gravel` | Terra Batida/Gravilha Fina | **$5.0$** | Muito esforço de tração. Rodas afundam ligeiramente. Evitar quase a todo custo. |
| `gravel`, `dirt`, `sand` | Gravilha Solta, Terra, Areia | **$20.0$** | Praticamente intransitável para qualquer tipo de auxílio de locomoção focado em rolamento. Atua quase como barreira. |

---

## 2. Penalização por Barreiras e Variáveis Estáticas

Aplicado transversalmente pela existência explícita de obstáculos na via.

| Tipo de Barreira (OSM / API) | Perfil Afetado | Peso (Penalty Point) | Lógica da Atribuição |
| :--- | :--- | :--- | :--- |
| `highway=steps` (Escadas) | Wheelchair, Stroller | **$10000.0$ (Infinito/Corte)** | Barreira arquitetónica intransponível (Hard Constraint). O peso torna impossível o algoritmo selecionar este caminho, independentemente da distância alternativa. |
| Passadeira s/ Sinal Sonoro | Invisual / Baixa Visão | **$10.0$** | Risco fatal. Exige perigo máximo de travessia. O motor deve desviar os invisuais para interseções sinalizadas ou com passeios passivos contínuos, admitindo uma rota dez vezes mais longa para garantir segurança. |
| `is_blocked=True` (Crowdsourcing) | Todos | **$99999.0$ (Corte Temporal)** | Feedback enviado pelos utilizadores (obras temporárias, carro estacionado no passeio). Corta a aresta temporariamente. |

---

## 3. A Lógica Matemática do Multiplicador `15.0` para a Inclinação

A justificação teórica em Engenharia Civil e Bio-mecânica para o uso do valor numérico `15.0` na função de penalização de inclinação é baseada na **Lei do Trabalho Dito Excesso** e no esgotamento da força humana de impulsão no plano inclinado.

### Porque não `2.0` ou `5.0`? (Estudo do Coeficiente)
Se definíssemos que uma rua com inclinação superior ao limite de um cadeirante (ex: > 8%) tivesse um peso de penalização leve (ex: `2.0`), o algoritmo leria uma subida íngreme de 100 metros como um percurso de "200 metros".
*   **O Problema do Peso Baixo:** Se a alternativa (a rua plana ideal) demorar um desvio longo pelo quarteirão inteiro (com 300 metros de distância física real), o algoritmo continuaria a escolher a rua íngreme (200 custo vs 300 custo). Isto **obrigaria a pessoa a subir a rua que fisicamente não consegue sustentar nas mãos**, pondo em causa a sua saúde ou causando despiste da cadeira de rodas "para trás", o que é um risco fatal.

### A Função Exponencial de Esforço
Na locomoção humana assistida, a energia requerida para vencer a gravidade numa superfície inclinada superior a 5% tem uma curva assintótica. A fadiga muscular dos braços cresce exponencialmente. 
*   Uma subida de $8\%$ é tolerável em distâncias muito curtas.
*   Uma rampa de $12\%$ sem corrimão é frequentemente intransponível independentemente da distância.

**Ao utilizar `Penalização = 15.0`:**
Dizemos matematicamente ao Grafo: *"Subir esta colina de 100 metros custa-te o equivalente a fazeres uma viagem plana ao longo de 1.5 Quilómetros (1500 metros)."* 

Este custo elevadíssimo força imediatamente o algoritmo de procura de caminhos (Dijkstra) a "desesperar" e pesquisar dezenas de alternativas, preferindo enviar o utilizador numa rota em ziguezague por avenidas marginais perfeitamente planas de 1.2 Km em vez de lutar com a rua reta e acidentada pela encosta da universidade de Vila Real. Este coeficiente foi testado como a "Golden Ratio" em sistemas de Micro-Routing para não interromper totalmente a rede, mas garantir um traçado puramente focado em evitar a exaustão física limitante.
