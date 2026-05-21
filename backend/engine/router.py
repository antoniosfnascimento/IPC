import logging
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import networkx as nx
import osmnx as ox

from engine.elevation import ElevationServiceError, annotate_graph_with_elevation
from models import RouteRequest, UserProfile
from sanitizer import FeatureSanitizer

log = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_DIR = os.path.join(BASE_DIR, "data", "osm_cache")
os.makedirs(CACHE_DIR, exist_ok=True)

EXCLUDED_HIGHWAY_TYPES = {
    "motorway", "motorway_link",
    "trunk", "trunk_link",
}

SNAP_ALLOWED_HIGHWAYS = {
    "footway", "path", "pedestrian", "living_street", "residential",
    "tertiary", "tertiary_link", "secondary", "secondary_link",
    "primary", "primary_link", "unclassified", "service", "cycleway",
    "steps", "track",
}

MAX_SNAP_DISTANCE_METERS = 250
ROUTE_MAX_NODE_DISTANCE_METERS = 500


class CityFlowRouter:
    """Builds and queries a walk-friendly graph enriched with real elevation."""

    def __init__(self, center_coords=(41.296, -7.746), radius=1500):
        self.center_coords = center_coords
        self.radius = radius

        ox.settings.use_cache = True
        ox.settings.cache_folder = CACHE_DIR
        self.G = None
        self._snap_subgraph = None

    def load_graph(self):
        log.info("Loading OSM graph (center=%s, radius=%dm)...", self.center_coords, self.radius)

        self.G = ox.graph_from_point(self.center_coords, dist=self.radius, network_type="walk")

        edges_to_remove = []
        for u, v, k, data in self.G.edges(keys=True, data=True):
            highway = data.get("highway", "")
            highway_set = set(highway) if isinstance(highway, list) else {highway}
            if highway_set & EXCLUDED_HIGHWAY_TYPES:
                edges_to_remove.append((u, v, k))
        self.G.remove_edges_from(edges_to_remove)

        isolated = list(nx.isolates(self.G))
        self.G.remove_nodes_from(isolated)
        log.info("Pruned %d motorway/trunk edges and %d isolated nodes.", len(edges_to_remove), len(isolated))

        try:
            annotate_graph_with_elevation(self.G)
        except ElevationServiceError as exc:
            log.warning("Elevation enrichment failed: %s. Slope filters will rely solely on OSM tags.", exc)

        self._snap_subgraph = self._build_snap_subgraph()
        log.info("Graph ready: %d nodes, %d edges.", self.G.number_of_nodes(), self.G.number_of_edges())

    def _build_snap_subgraph(self):
        """Subgraph containing only edges where it is safe to place an A/B marker."""
        keep_edges = []
        for u, v, k, data in self.G.edges(keys=True, data=True):
            highway = data.get("highway", "")
            highway_set = set(highway) if isinstance(highway, list) else {highway}
            if highway_set & SNAP_ALLOWED_HIGHWAYS:
                keep_edges.append((u, v, k))
        subgraph = self.G.edge_subgraph(keep_edges).copy()
        return subgraph

    def snap_point(self, coords: tuple) -> dict:
        if self.G is None or self._snap_subgraph is None:
            self.load_graph()

        node_id, distance = ox.distance.nearest_nodes(
            self._snap_subgraph, X=coords[1], Y=coords[0], return_dist=True,
        )

        if distance > MAX_SNAP_DISTANCE_METERS:
            return {
                "valid": False,
                "snapped_coords": None,
                "distance_meters": distance,
                "message": (
                    f"Esse ponto está a {distance:.0f} m de uma rua pedonal. "
                    "Por favor clica mais perto de uma via acessível."
                ),
            }

        node_data = self._snap_subgraph.nodes[node_id]
        return {
            "valid": True,
            "snapped_coords": (node_data["y"], node_data["x"]),
            "distance_meters": distance,
            "adjusted": distance > 5.0,
            "message": None,
        }

    def _resolve_grade(self, data: dict) -> float:
        """Prefer the elevation-derived grade; fall back to the OSM `incline` tag."""
        grade_abs = data.get("grade_abs")
        if grade_abs is not None:
            try:
                return float(grade_abs)
            except (TypeError, ValueError):
                pass

        incline_raw = data.get("incline")
        if isinstance(incline_raw, list):
            incline_raw = incline_raw[0]
        if not incline_raw:
            return 0.0
        incline_str = str(incline_raw).replace("%", "").strip()
        incline_val = FeatureSanitizer.parse_float(incline_str, 0.0)
        return abs(incline_val) / 100.0

    def _calculate_edge_weight(self, data, profile: UserProfile) -> float:
        length = FeatureSanitizer.parse_float(data.get("length"), 1.0)
        penalty_total = 1.0

        highway = data.get("highway", "")
        if isinstance(highway, list):
            highway = highway[0]

        if profile.avoid_stairs and highway == "steps":
            penalty_total *= 10000.0

        surface_raw = data.get("surface", "")
        if isinstance(surface_raw, list):
            surface_raw = surface_raw[0]
        surface = FeatureSanitizer.normalize_surface(surface_raw)
        if surface != "unknown" and surface not in profile.surface_preference:
            penalty_total *= 3.5

        grade_abs = self._resolve_grade(data)
        if grade_abs > profile.max_incline:
            penalty_total *= 15.0
        elif grade_abs > profile.max_incline * 0.75:
            penalty_total *= 3.0

        width_raw = data.get("width")
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
            data["custom_weight"] = self._calculate_edge_weight(data, request.profile)

        start_node, start_dist = ox.distance.nearest_nodes(
            self.G, X=request.start_coords[1], Y=request.start_coords[0], return_dist=True,
        )
        end_node, end_dist = ox.distance.nearest_nodes(
            self.G, X=request.end_coords[1], Y=request.end_coords[0], return_dist=True,
        )

        if start_dist > ROUTE_MAX_NODE_DISTANCE_METERS or end_dist > ROUTE_MAX_NODE_DISTANCE_METERS:
            FeatureSanitizer.log_warning(
                f"Route blocked: start/end point is detached from the walkable network "
                f"(start={start_dist:.1f}m, end={end_dist:.1f}m)."
            )
            return [], 0.0, 0.0

        try:
            route_nodes = nx.shortest_path(
                self.G, start_node, end_node, weight="custom_weight", method="bellman-ford",
            )
        except nx.NetworkXNoPath:
            FeatureSanitizer.log_warning(
                f"No viable path between {request.start_coords} and {request.end_coords}."
            )
            return [], 0.0, 0.0

        total_distance = 0.0
        max_route_incline = 0.0
        route_coords = []

        if route_nodes:
            first_node_data = self.G.nodes[route_nodes[0]]
            route_coords.append((first_node_data["y"], first_node_data["x"]))

        for i in range(len(route_nodes) - 1):
            u_node = route_nodes[i]
            v_node = route_nodes[i + 1]

            edge_data_dict = self.G.get_edge_data(u_node, v_node)
            if not edge_data_dict:
                continue

            best_edge_key = min(
                edge_data_dict,
                key=lambda k: edge_data_dict[k].get("custom_weight", float("inf")),
            )
            edge_data = edge_data_dict[best_edge_key]

            edge_length = FeatureSanitizer.parse_float(edge_data.get("length"), 1.0)
            grade_abs = self._resolve_grade(edge_data)
            if grade_abs > max_route_incline:
                max_route_incline = grade_abs

            total_distance += edge_length

            if "geometry" in edge_data:
                for point in list(edge_data["geometry"].coords):
                    route_coords.append((point[1], point[0]))
            else:
                node_data = self.G.nodes[v_node]
                route_coords.append((node_data["y"], node_data["x"]))

        return route_coords, total_distance, max_route_incline
