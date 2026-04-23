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
        
        
        ox.settings.use_cache = True
        ox.settings.cache_folder = './data/osm_cache'
        self.G = None

    def load_graph(self):
        print(f"A carregar o grafo OSM (centro: {self.center_coords}, raio: {self.radius}m)...")
        
        
        self.G = ox.graph_from_point(self.center_coords, dist=self.radius, network_type='walk')
        print("Grafo carregado com sucesso.")

    def _calculate_edge_weight(self, u, v, data, profile: UserProfile) -> float:
        
        length = FeatureSanitizer.parse_float(data.get('length'), 1.0)
        
        penalty_total = 1.0
        
        highway = data.get('highway', '')
        if isinstance(highway, list):
            highway = highway[0]
            
        
        if profile.avoid_stairs and highway == 'steps':
            penalty_total = 10000.0
            
        
        surface_raw = data.get('surface', '')
        if isinstance(surface_raw, list):
            surface_raw = surface_raw[0]
        surface = FeatureSanitizer.normalize_surface(surface_raw)
        
        
        if surface != 'unknown' and surface not in profile.surface_preference:
            penalty_total *= 3.5
            
        
        incline_raw = data.get('incline')
        if isinstance(incline_raw, list):
            incline_raw = incline_raw[0]
            
        if incline_raw:
            incline_str = str(incline_raw).replace('%', '').strip()
            incline_val = FeatureSanitizer.parse_float(incline_str, 0.0)
            
            
            if abs(incline_val) / 100.0 > profile.max_incline:
                penalty_total *= 15.0
                
        
        width_raw = data.get('width')
        if isinstance(width_raw, list):
            width_raw = width_raw[0]
        width = FeatureSanitizer.sanitize_width(width_raw)
        
        
        if width < profile.min_width:
            penalty_total *= 5.0
            
        return length * penalty_total

    def get_route(self, request: RouteRequest) -> tuple:
        if self.G is None:
            self.load_graph()
            
        
        for u, v, k, data in self.G.edges(keys=True, data=True):
            weight = self._calculate_edge_weight(u, v, data, request.profile)
            self.G[u][v][k]['custom_weight'] = weight

        
        
        start_node_info = ox.distance.nearest_nodes(self.G, X=request.start_coords[1], Y=request.start_coords[0], return_dist=True)
        end_node_info = ox.distance.nearest_nodes(self.G, X=request.end_coords[1], Y=request.end_coords[0], return_dist=True)
        
        start_node = start_node_info[0]
        start_dist = start_node_info[1]
        
        end_node = end_node_info[0]
        end_dist = end_node_info[1]
        
        
        if start_dist > 500 or end_dist > 500:
            FeatureSanitizer.log_warning(f"Rota bloqueada: O ponto de partida e/ou de chegada está fora de área e isolado da rede viária (Distâncias P:{start_dist:.1f}m, C:{end_dist:.1f}m).")
            return [], 0.0, 0.0

            
        try:
            
            route_nodes = nx.shortest_path(self.G, start_node, end_node, weight='custom_weight', method='bellman-ford')
            
            
            total_distance = 0.0
            max_route_incline = 0.0
            route_coords = [request.start_coords]
            
            if route_nodes:
                first_node_data = self.G.nodes[route_nodes[0]]
                route_coords.append((first_node_data['y'], first_node_data['x']))

            for i in range(len(route_nodes) - 1):
                u_node = route_nodes[i]
                v_node = route_nodes[i+1]
                
                
                edge_data_dict = self.G.get_edge_data(u_node, v_node)
                if not edge_data_dict:
                    continue
                    
                
                best_edge_key = min(edge_data_dict, key=lambda k: edge_data_dict[k].get("custom_weight", float('inf')))
                edge_data = edge_data_dict[best_edge_key]
                
                edge_weight = edge_data.get('custom_weight', 0)
                edge_length = FeatureSanitizer.parse_float(edge_data.get('length'), 1.0)
                
                
                incline_raw = edge_data.get('incline')
                if isinstance(incline_raw, list):
                    incline_raw = incline_raw[0]
                if incline_raw:
                    incline_str = str(incline_raw).replace('%', '').strip()
                    incline_val = FeatureSanitizer.parse_float(incline_str, 0.0)
                    incline_decimal = abs(incline_val) / 100.0
                    if incline_decimal > max_route_incline:
                        max_route_incline = incline_decimal
                
                
                total_distance += edge_length
                
                if edge_length > 0 and (edge_weight / edge_length) >= 14.5:
                    FeatureSanitizer.log_warning(f"Rota bloqueada: barreira arquitetónica (ex: rampas > limite) detetada entre os nós {u_node} e {v_node}.")
                    return [], 0.0, 0.0

                if 'geometry' in edge_data:
                    for point in list(edge_data['geometry'].coords):
                        route_coords.append((point[1], point[0]))
                else:
                    node_data = self.G.nodes[v_node]
                    route_coords.append((node_data['y'], node_data['x']))
            
            route_coords.append(request.end_coords)
            
            return route_coords, total_distance, max_route_incline
            
        except nx.NetworkXNoPath:
            FeatureSanitizer.log_warning(f"Não existe um caminho estrutural válido entre {request.start_coords} e {request.end_coords}.")
            return [], 0.0, 0.0
