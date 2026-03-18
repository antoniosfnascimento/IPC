# Dicionário de Dados: Perfis de Utilizador e Restrições Físicas

Esta tabela especifica as "Hard Constraints" (constantes matemáticas e booleanas baseadas em manuais de acessibilidade universal) que o Motor Geoespacial vai aplicar a cada aresta do grafo OSM, dependendo do perfil escolhido. Estes parâmetros balizam a Heurística de Penalização de Dijkstra.

| Perfil de Utilizador | Limitação Base | Inclinação Máxima (`max_incline`) | Largura Mínima (`min_width`) | Escadas/Degraus (`avoid_stairs`) | Superfícies Preferenciais (`surface_preference`) | Fator Multiplicador (Esforço) | Justificação Técnica |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Cadeira de Rodas** | Motores/Rodados | $8\%$ ($0.08$) | $1.20m$ | `True` | `paved`, `asphalt`, `concrete`, `paving_stones` | x15 em inclinações > 5% | Restrição W3C para rampas e obrigatório evitar piso não consolidado (`gravel`, `dirt`) devido ao atrito. |
| **Mobilidade Reduzida** (Andarilho/Muletas) | Instabilidade/Esforço | $10\%$ ($0.10$) | $0.90m$ | `True` | `paved`, `asphalt`, `concrete`, `compacted` | x10 em inclinações > 8% | Menor tolerância a distâncias, mas passagem viável por larguras inferiores a cadeiras de rodas. |
| **Idoso** | Fadiga/Cardíaco | $12\%$ ($0.12$) | $0.80m$ | `False` (mas evitar se > 5 degraus) | `paved`, `asphalt`, `concrete` | x20 em escadas, x5 em subidas longas | Maior foco na exaustão física em subidas do que em largura da via. Degraus são possíveis, mas fortemente penalizados. |
| **Carrinho de Bebé** | Rodados Pequenos/Vibração | $15\%$ ($0.15$) | $0.90m$ | `True` | `paved`, `asphalt`, `concrete` | x5 em buracos (`cobblestone`) | Menor restrição cardíaca que "Idoso", mas forte aversão a pisos vibro-acústicos (empedrado/paralelos de Vila Real) por conforto do bebé. |
| **Invisibilidade/Baixa Visão** | Referências Táteis | $20\%$ ($0.20$) | $0.90m$ | `False` | Qualquer | N/A | Foco não está no esforço, mas na necessidade de evitar passeios rebaixados não nivelados (ou uso de pavimento tátil). |
| **Focado na Distância** (Standard) | Nenhuma | $30\%$ ($0.30$) | $0.50m$ | `False` | Qualquer | x1 | Usa exatamente a métrica de "Distância Mais Curta" pura do Dijkstra sem penalizações de hardware/esforço. |

**Notas de Engenharia (Backend `router.py`):**
*   **Declive (`incline`):** No OSM, o valor de `incline` é frequentemente armazenado com o sinal de descida (`-5%`) ou subida (`5%`) dependendo do sentido da via (direção da aresta [u, v]). O motor usa a função `abs()` (valor absoluto) para aplicar a restrição de fadiga, independentemente da direção no grafo para simplificação.
*   **Largura (`width`):** Ruas em Portugal (especialmente centros históricos como Vila Real) muitas vezes **não** têm a tag `width` preenchida no OSM. Se tentar filtrar em demasia, o grafo pode "partir-se" não gerando rotas possíveis, resultando num Erro HTTP 424. Uma solução técnica é colocar um *fallback*: se `width == None`, assumir um valor de default (ex: $1.0m$) com base no tipo de rodovia (`footway` = $1.0m$, `residential` = $1.5m$).
