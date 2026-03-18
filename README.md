# CityFlow Vila Real - Navegação Cívica e Inclusiva

## Descrição
Solução de mobilidade assistida para perfis vulneráveis (Sénior e Cadeira de Rodas) em ambiente urbano.

## Tecnologias
- **FastAPI** (Python)
- **React** (Vite / Tailwind v4)
- **OSMnx**
- **Leaflet**

## A Lógica Matemática
O motor de rotas utiliza algoritmos de grafos (Dijkstra) onde o peso de cada aresta ($W_e$) penaliza trajetos não acessíveis ou perigosos. A fórmula base para o cálculo da resistência/esforço do trajeto é a seguinte:

$$W_e = \text{comprimento} \times \text{penalização total (inclinação + piso + escadas)}$$

## Funcionalidades
- **Bounding Box de segurança:** Restrição rigorosa do espaço geográfico processado para garantir estabilidade e resposta rápida.
- **Cálculo de tempo cinético adaptado:** As estimativas de tempo são calibradas perante a realidade de locomoção de seniores e utilizadores de cadeiras de rodas.
- **Análise de risco de elevação:** O sistema identifica e bloqueia rotas com inclinações acima dos limites seguros para o utilizador.

## Instalação

### Backend (Python API)
Vais precisar de instalar as dependências e correr o servidor local FastAPI:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend (React App)
Com o backend a correr, abre um novo terminal e instala/inicia a interface:
```bash
cd frontend
npm install
npm run dev
```
