# Dicionário de Dados: Perfis de Utilizador e Restrições Físicas

Esta tabela especifica as *hard constraints* (constantes matemáticas e booleanas baseadas em manuais de acessibilidade universal) que o motor geoespacial aplica a cada aresta do grafo OSM, dependendo do perfil escolhido. Estes parâmetros parametrizam a heurística de penalização do Bellman-Ford.

| Perfil de utilizador | Limitação base | Inclinação máxima (`max_incline`) | Largura mínima (`min_width`) | Escadas (`avoid_stairs`) | Superfícies preferenciais (`surface_preference`) | Multiplicador de esforço | Justificação técnica |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Cadeira de rodas** | Motora / rodados | 8 % (0,08) | 1,20 m | `True` | `paved`, `asphalt`, `concrete`, `paving_stones` | ×15 em inclinações > 5 % | Norma W3C para rampas e obrigatório evitar piso não consolidado (`gravel`, `dirt`) devido ao atrito. |
| **Mobilidade reduzida** (andarilho/muletas) | Instabilidade / esforço | 10 % (0,10) | 0,90 m | `True` | `paved`, `asphalt`, `concrete`, `compacted` | ×10 em inclinações > 8 % | Menor tolerância à distância, mas é viável passar em larguras inferiores às de uma cadeira de rodas. |
| **Sénior** | Fadiga / cardíaco | 12 % (0,12) | 0,80 m | `False` (mas evitar se > 5 degraus) | `paved`, `asphalt`, `concrete` | ×20 em escadas, ×5 em subidas longas | Maior foco na exaustão física em subidas do que na largura da via. Escadas são possíveis mas fortemente penalizadas. |
| **Carrinho de bebé** | Rodas pequenas / vibração | 15 % (0,15) | 0,90 m | `True` | `paved`, `asphalt`, `concrete` | ×5 em buracos (`cobblestone`) | Menor restrição cardíaca do que "sénior", mas forte aversão a pisos vibratórios (a calçada de Vila Real) por conforto do bebé. |
| **Baixa visão** | Referências táteis | 20 % (0,20) | 0,90 m | `False` | Qualquer | n/d | O foco não está no esforço, mas em evitar passeios rebaixados não nivelados (ou usar pavimento tátil). |
| **Focado na distância** (standard) | Nenhuma | 30 % (0,30) | 0,50 m | `False` | Qualquer | ×1 | Usa puramente o menor caminho do Bellman-Ford sem penalizações de hardware ou esforço. |

**Notas de engenharia (`router.py`):**
*   **Declive (`incline`):** No OSM, o valor de `incline` é frequentemente guardado com o sinal de descida (`-5%`) ou subida (`5%`) consoante a direção da aresta. O motor usa `abs()` para que a restrição de fadiga seja aplicada independentemente da direção. Como a tag OSM `incline` é esparsa em Vila Real, o motor recorre a um declive por aresta calculado a partir da API de elevação OpenTopoData (conjunto EU-DEM 25 m).
*   **Largura (`width`):** As ruas em Portugal (sobretudo centros históricos como Vila Real) muitas vezes *não* têm a tag `width` preenchida no OSM. Filtrar com demasiada exigência parte o grafo e leva a HTTP 424. O fallback é assumir 0,5 m para valores em falta e confiar no multiplicador para empurrar o *routing* para ruas mapeadas.
