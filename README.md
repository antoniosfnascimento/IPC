# CityFlow — Navegação Cívica Inclusiva

## Visão geral
Solução de mobilidade assistida para perfis urbanos vulneráveis (séniores, utilizadores de cadeira de rodas). O motor reescreve o clássico "caminho mais curto" como "caminho mais viável", injetando penalizações de acessibilidade em cada aresta do grafo OpenStreetMap.

## Cidades suportadas
O MVP carrega duas cidades em paralelo. O frontend permite alternar entre elas; ambos os grafos são pré-aquecidos no arranque do backend.

| Cidade | Centro (lat, lon) | Raio | Justificação |
| :--- | :--- | :--- | :--- |
| **Vila Real** (predefinida) | 41.296, -7.746 | 1,5 km | Base académica ligada à investigação de utilizadores conduzida na UTAD (personas João, Maria, Ricardo). |
| **Paris (Châtelet)** | 48.8584, 2.347 | 1,5 km | Demonstração: dados OSM densos e 31,5 % das arestas com a tag `smoothness`, pelo que cada filtro altera visivelmente a rota. Ver `docs/documentacaoPlataforma/Multi_City_Viability_Report.md` para os números comparativos. |

## Stack tecnológica
- **FastAPI** (Python)
- **React** (Vite + Tailwind v4)
- **OSMnx** + **NetworkX** para processamento de grafos
- **Leaflet** para a interface do mapa
- **OpenTopoData** (Modelo Digital de Elevação gratuito) para enriquecimento real do declive

## Como funciona a matemática do *routing*
O motor executa Bellman-Ford sobre a rede pedonal do OSM. Cada peso de aresta $W_e$ multiplica o comprimento do segmento por uma penalização de acessibilidade:

$$W_e = \text{comprimento} \times \text{penalização total (declive + piso + escadas + largura)}$$

O declive é a variável mais importante — e a maior fonte de risco oculto. Quando as tags `incline` do OSM são esparsas (em Vila Real cobrem ~1 % das arestas), o backend consulta o conjunto **OpenTopoData EU-DEM** no arranque para calcular o declive real por aresta a partir das elevações dos nós. É assim que a subida à UTAD passa a ser detetada corretamente em vez de aparecer silenciosamente como 0 %.

## Funcionalidades
- **Seletor multi-cidade** — alterna entre Vila Real e Paris a partir da barra lateral; o mapa, o destino do *snap* e o motor de rotas seguem automaticamente.
- **Análise real do declive** — o gradiente derivado da elevação penaliza arestas íngremes, com um multiplicador suave de "perto do limite" para além do corte rígido de 15×.
- **Snap-point pedonal** — os pontos A/B são projetados sobre a aresta pedonal mais próxima (até 250 m). Autoestradas, vias rápidas e terreno sem rede pedonal são excluídos.
- **Estimativa cinemática de tempo** — a velocidade de marcha é ajustada para o ritmo de um sénior ou de uma pessoa em cadeira de rodas.
- **Caixa delimitadora de cobertura** — mantém o grafo pequeno (raio de 1,5 km) e a resposta abaixo de ~1 s depois do primeiro arranque.

## Instalação

### Backend (API Python)
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

O primeiro arranque aquece ambos os grafos de cidade e obtém as elevações através do OpenTopoData (gratuito, sem chave) — conta com ~1 minuto no total. O OSMnx coloca os grafos em cache local; arranques seguintes são imediatos.

### Frontend (aplicação React)
Com o backend a correr, num novo terminal:
```bash
cd frontend
npm install
npm run dev
```

## Scripts de arranque
- macOS / Linux: `./start.sh` e `./stop.sh`
- Windows: `start.bat` (recomendado) ou `./start.ps1` e `./stop.ps1`
