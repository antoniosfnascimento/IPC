import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import osmnx as ox
import networkx as nx
from models import UserProfile, RouteRequest
from sanitizer import FeatureSanitizer

class CityFlowRouter:
    def __init__(self, center_coords=(41.296, -7.746), radius=1500):
        self.center_coords = center_coords
        self.radius = radius
        
        # Ativar a cache local do OSMnx
        ox.settings.use_cache = True
        ox.settings.cache_folder = './data/osm_cache'
        self.G = None

    def load_graph(self):
        print(f"A carregar o grafo OSM (centro: {self.center_coords}, raio: {self.radius}m)...")
        # TODO (Future): Expandir o carregamento do grafo do OSM para Vila Real inteira e Distrito quando o MVP estiver validado.
        # Rede 'walk' reflete percursos pedestres
        self.G = ox.graph_from_point(self.center_coords, dist=self.radius, network_type='walk')
        print("Grafo carregado com sucesso.")

    def _calculate_edge_weight(self, u, v, data, profile: UserProfile) -> float:
        # Base (Comprimento da via)
        length = FeatureSanitizer.parse_float(data.get('length'), 1.0)
        
        penalty_total = 1.0
        
        highway = data.get('highway', '')
        if isinstance(highway, list):
            highway = highway[0]
            
        # 1. Escadas - Peso mandatado: 10000
        if profile.avoid_stairs and highway == 'steps':
            penalty_total = 10000.0
            
        # 2. Superfície
        surface_raw = data.get('surface', '')
        if isinstance(surface_raw, list):
            surface_raw = surface_raw[0]
        surface = FeatureSanitizer.normalize_surface(surface_raw)
        
        # Penalização se piso não for preferencial (Multiplicador = 3.5)
        if surface != 'unknown' and surface not in profile.surface_preference:
            penalty_total *= 3.5
            
        # 3. Inclinação
        incline_raw = data.get('incline')
        if isinstance(incline_raw, list):
            incline_raw = incline_raw[0]
            
        if incline_raw:
            incline_str = str(incline_raw).replace('%', '').strip()
            incline_val = FeatureSanitizer.parse_float(incline_str, 0.0)
            
            # Converter a taxa da diretiva (ex: 5 -> 0.05) vs (max_incline=0.08)
            if abs(incline_val) / 100.0 > profile.max_incline:
                penalty_total *= 15.0
                
        # 4. Largura Defensiva
        width_raw = data.get('width')
        if isinstance(width_raw, list):
            width_raw = width_raw[0]
        width = FeatureSanitizer.sanitize_width(width_raw)
        
        # Aplicamos uma penalidade para vias estreitas não especificadas explicitamente nas requests, mas defensivas
        if width < profile.min_width:
            penalty_total *= 5.0
            
        return length * penalty_total

    def get_route(self, request: RouteRequest) -> tuple:
        if self.G is None:
            self.load_graph()
            
        # 1. Iterar sobre as arestas do grafo e aplicar o FeatureSanitizer e as penalizações W_e
        for u, v, k, data in self.G.edges(keys=True, data=True):
            weight = self._calculate_edge_weight(u, v, data, request.profile)
            self.G[u][v][k]['custom_weight'] = weight

        # 2. Mapear coordenadas do utilizador para os nós matemáticos do OSM
        # O distance.nearest_nodes cruza com um array ou tuple. Ponto = (lat, lon), X=Lon, Y=Lat
        start_node_info = ox.distance.nearest_nodes(self.G, X=request.start_coords[1], Y=request.start_coords[0], return_dist=True)
        end_node_info = ox.distance.nearest_nodes(self.G, X=request.end_coords[1], Y=request.end_coords[0], return_dist=True)
        
        start_node = start_node_info[0]
        start_dist = start_node_info[1]
        
        end_node = end_node_info[0]
        end_dist = end_node_info[1]
        
        # Inviabilidade: Evitar o "snapping" milagreiro se o ponto pedido dista mais de 500m da rede primária
        if start_dist > 500 or end_dist > 500:
            FeatureSanitizer.log_warning(f"Rota bloqueada: O ponto de partida e/ou de chegada está fora de área e isolado da rede viária (Distâncias P:{start_dist:.1f}m, C:{end_dist:.1f}m).")
            return [], 0.0, 0.0

            # 3. Descobrir a linha mais barata baseada no custom_weight
        try:
            # MultiDiGraph requires careful handling of edge keys
            route_nodes = nx.shortest_path(self.G, start_node, end_node, weight='custom_weight', method='bellman-ford')
            
            # 4. Verificar o limite de Inviabilidade e calcular métricas
            total_distance = 0.0
            max_route_incline = 0.0
            for i in range(len(route_nodes) - 1):
                u_node = route_nodes[i]
                v_node = route_nodes[i+1]
                
                # O NetworkX devolve um dicionário de chaves do MultiDiGraph
                edge_data_dict = self.G.get_edge_data(u_node, v_node)
                if not edge_data_dict:
                    continue
                    
                # Extrair os dados da aresta usada (a que tem menor peso)
                best_edge_key = min(edge_data_dict, key=lambda k: edge_data_dict[k].get("custom_weight", float('inf')))
                edge_data = edge_data_dict[best_edge_key]
                
                edge_weight = edge_data.get('custom_weight', 0)
                edge_length = FeatureSanitizer.parse_float(edge_data.get('length'), 1.0)
                
                # Monitorar Inclinação Extrema
                incline_raw = edge_data.get('incline')
                if isinstance(incline_raw, list):
                    incline_raw = incline_raw[0]
                if incline_raw:
                    incline_str = str(incline_raw).replace('%', '').strip()
                    incline_val = FeatureSanitizer.parse_float(incline_str, 0.0)
                    incline_decimal = abs(incline_val) / 100.0
                    if incline_decimal > max_route_incline:
                        max_route_incline = incline_decimal
                
                # Acumula a distância
                total_distance += edge_length
                
                # Se a penalidade bruta for >= 15.0, significa barreira intransponível 
                # (ex: Escadas = 10000, ou Inclinação > Limite = 15.0)
                if edge_length > 0 and (edge_weight / edge_length) >= 14.5:
                    FeatureSanitizer.log_warning(f"Rota bloqueada: barreira arquitetónica (ex: rampas > limite) detetada entre os nós {u_node} e {v_node}.")
                    return [], 0.0, 0.0
            
            # 5. Converter em array de arrays: [lat, lon]
            route_coords = []
            for node in route_nodes:
                node_data = self.G.nodes[node]
                route_coords.append((node_data['y'], node_data['x']))
                
            return route_coords, total_distance, max_route_incline
            
        except nx.NetworkXNoPath:
            FeatureSanitizer.log_warning(f"Não existe um caminho estrutural válido entre {request.start_coords} e {request.end_coords}.")
            return [], 0.0, 0.0
