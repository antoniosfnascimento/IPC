# 📜 Registo Integral do Projeto: CityFlow Inclusivo

## 1. Contextualização Inicial
**Utilizador:** 
Tenho uma UC chamada Interação Pessoa Computador e após as etapas que já desenvolvemos (que vais poder consultar) temos de desenvolver uma aplicação web (MVP) que reuna as nossas principais preocupações detetadas durante o planeamento. Basicamente, a ideia é desenvolver uma app web (desde as primeiras ideias até ao MVP) tendo em conta fatores como acessibilidade e usabilidade (diferenciada). Fizemos um conjunto de desafios (pequenas tarefas) até à jornada do utilizador, mas, a partir daqui, o grupo decidiu fazer primeiro o MVP e depois fazer os mockups e as wireframes a seguir. Vou enviar-te toda a documentação que foi fornecida pelos docentes da UC até agora, todos os documentos sobre tarefas e desafios e o trabalho que foi feito pelo grupo até agora. O objetivo é que, com isto, tenhas o melhor contexto possível para criamos juntos (aos poucos, conforme necessário) a aplicação web que será usada como MVP. Percebeste?

**Assistente AI:**
Com certeza, percebi perfeitamente o contexto. Tenho agora uma visão clara do projeto "CityFlow Inclusivo" e das diretrizes da UC de Interação Pessoa-Computador (IPC). Pelo que analisei nos documentos e imagens que enviaste, o vosso foco é uma aplicação de mobilidade urbana focada em acessibilidade total... (Resumo das preocupações centrais e proposta de stack tecnológica).

---

## 2. Definição da Stack e Primeiros Filtros
**Utilizador:**
Inicialmente pensamos em usar o ASP.NET MVC por já conhecermos bem, mas por causa das APIs (vamos obrigatoriamente precisar de usar para obtermos os dados de localização e dos problemas de mobilidade (específicos a cada situação) para cada local do mapa) pensamos em usar python. Mas estamos abertos a usar react, typesript, node, etc. Este projeto tem essa vantagem: não tem nenhuma restrição ou obrigação tecnologia associada vinda de superiores. A principal funcionalidade é a visualização do mapa e a capacidade de conseguir obter uma rota personalizada para cada pessoa consoante o tipo de probleam/deificiencia selecionada... (Exemplos de cadeira de rodas vs ciclista e inclinação).

**Assistente AI:**
(Propõe a stack: FastAPI para Backend e React para Frontend. Explica a lógica de pesos customizados no motor de grafos usando OSMnx e NetworkX).

---

## 3. Estruturação da Lógica de Negócio e Backend
**Utilizador:**
Gostava de trabalhar contigo um pouco mais sobre mais alguns filtros e opções. Dei como exemplo a cadeira de rodas e o ciclista, mas existem vários tipos de filtros (e sub-filtros) com várias condicionantes. Dado que esse será o foco da app... começa pelas fundações e pelo que seria mais difícil de estruturar... depois de fazeres um trabalho base de backend podes incorporar o frontend...

**Assistente AI:**
(Estabelece a lógica de custo dinâmico. Define os perfis Motor, Visual e de Baixo Esforço. Cria a estrutura de classes inicial: `MobilityConstraints` e `ProfileWeightEngine`).

---

## 4. Estrutura de Ficheiros e Ambiente
**Utilizador:**
Diz-me como será necessário que os ficheiros deste projeto sejam colocados num diretório no meu SO e executados. Serei eu a colocá-los (a copiar do teus "pedaços" de código que recomendaste) nos ficheiros através do VSCode ou depois eu baixo o projeto completo?

**Assistente AI:**
(Define a estrutura de pastas: `backend/`, `frontend/`, `data/`. Fornece os primeiros ficheiros funcionais: `requirements.txt`, `engine/models.py`, `engine/router.py`).

---

## 5. Implementação da API e Correção para Mac
**Utilizador:**
(Envia print da estrutura e logs de erro: `zsh: command not found: python`. Indica que usa macOS mas o projeto deve ser cross-platform).

**Assistente AI:**
(Corrige os comandos para `python3` e `pip3`. Fornece o código do servidor principal `backend/main.py` ligando a API ao motor de rotas).

---

## 6. Depuração: O Erro "Internal Server Error" e a Cache
**Utilizador:**
(Relata que o carregamento do mapa de Vila Real está a demorar e envia logs de erro 500 no terminal e browser. Identifica falta da biblioteca `scikit-learn`).

**Assistente AI:**
(Explica a necessidade de `scikit-learn` para pesquisas espaciais. Implementa o `_parse_float` para lidar com dados "sujos" do OSM. Adiciona sistema de cache persistente no `router.py` para evitar downloads repetitivos).

---

## 7. Automação de Setup (O Botão Único)
**Utilizador:**
...Não tem uma forma de precisar apenas de um comando no terminal para que todos esses comandos e configurações da app sejam feitas automaticamente? Imagina que vou entregar este projeto a uma pessoa. Ela iria ao terminal e iria escrever (na root do projeto): python3 main.py (mesmo que fosse no windows) e o projeto deveria funcionar dessa forma.

**Assistente AI:**
(Cria o script `run_backend.py` na raiz do projeto, capaz de detetar o SO, criar o `venv`, instalar as dependências e lançar o servidor).

---

## 8. Otimização Radical de Performance
**Utilizador:**
(Reporta que o carregamento ainda demora 10 a 15 minutos e erros de `mismatch` no `init`. Os warnings de importação no VSCode persistem).

**Assistente AI:**
(Otimiza o `router.py` para carregar apenas um raio de 1.5km do centro de Vila Real em vez da cidade toda. Corrige a inicialização do `router` no `main.py`. Explica como configurar o interpretador do VSCode para remover os avisos).

---

## 9. A "Bíblia do Projeto" (Documentação Técnica Final)
**Utilizador:**
Gostava que fizesses agora a documentação do projeto inteiro... como se quisesse vender a documentação para que até um estagiário conseguisse implementar... diagramas de classes, ER, justificações de tecnologia...

**Assistente AI:**
(Gera o documento `DOCUMENTATION.md` versão 1.1, detalhando Logline, Justificação de Stack, Requisitos Funcionais e Não Funcionais, Diagrama de Classes e Fórmulas Matemáticas de Penalização).

---

## 10. Código Base Final (Versão Atual no Projeto)

### `backend/engine/router.py`
```python
import osmnx as ox
import networkx as nx
import re
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cache_dir = os.path.join(BASE_DIR, "data", "osm_cache")
os.makedirs(cache_dir, exist_ok=True)

ox.settings.use_cache = True
ox.settings.cache_folder = cache_dir

class CityFlowRouter:
    def __init__(self):
        self.center_point = (41.296, -7.746)
        self.dist = 1500 
        try:
            print(f"--- Carregando Centro de Vila Real (raio 1.5km)... ---")
            self.G = ox.graph_from_point(self.center_point, dist=self.dist, network_type='walk')
            print("--- Mapa carregado e em cache! ---")
        except Exception as e:
            print(f"ERRO ao carregar mapa: {e}")
            raise

    def _parse_float(self, value, default=0.0):
        if value is None: return default
        try:
            match = re.search(r"[-+]?\d*\.\d+|\d+", str(value))
            return float(match.group()) if match else default
        except:
            return default

    def get_route(self, start_coords, end_coords, profile):
        try:
            orig_node = ox.distance.nearest_nodes(self.G, start_coords[1], start_coords[0])
            dest_node = ox.distance.nearest_nodes(self.G, end_coords[1], end_coords[0])
            for u, v, k, data in self.G.edges(data=True, keys=True):
                length = data.get('length', 1.0)
                penalty = 1.0
                if profile.avoid_stairs and data.get('highway') == 'steps':
                    penalty = 1000.0
                surface = str(data.get('surface', 'unknown')).lower()
                if profile.surface_preference and surface not in [s.lower() for s in profile.surface_preference]:
                    penalty *= 3.0
                incline = self._parse_float(data.get('incline'), 0.0)
                if abs(incline) > profile.max_incline:
                    penalty *= 15.0
                self.G[u][v][k]['custom_weight'] = length * penalty
            route = nx.shortest_path(self.G, orig_node, dest_node, weight='custom_weight')
            return [[self.G.nodes[node]['y'], self.G.nodes[node]['x']] for node in route]
        except Exception as e:
            return {"error": str(e)}
```

### `run_backend.py` (Root)
```python
import os
import subprocess
import sys
import platform

def run():
    is_windows = platform.system() == "Windows"
    root_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(root_dir, "backend")
    venv_dir = os.path.join(backend_dir, "venv")
    
    if is_windows:
        venv_python = os.path.join(venv_dir, "Scripts", "python.exe")
        uvicorn_bin = os.path.join(venv_dir, "Scripts", "uvicorn.exe")
    else:
        venv_python = os.path.join(venv_dir, "bin", "python")
        uvicorn_bin = os.path.join(venv_dir, "bin", "uvicorn")

    if not os.path.exists(venv_dir):
        print("--- [1/3] Criando ambiente virtual... ---")
        subprocess.run([sys.executable, "-m", "venv", venv_dir], check=True)

    print("--- [2/3] Atualizando bibliotecas... ---")
    subprocess.run([venv_python, "-m", "pip", "install", "--upgrade", "pip"], check=True)
    subprocess.run([venv_python, "-m", "pip", "install", "-r", os.path.join(backend_dir, "requirements.txt")], check=True)

    print("--- [3/3] Iniciando CityFlow em http://localhost:8000 ---")
    os.chdir(backend_dir)
    try:
        subprocess.run([uvicorn_bin, "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"])
    except KeyboardInterrupt:
        print("\n--- Servidor desligado. ---")

if __name__ == "__main__":
    run()
```
