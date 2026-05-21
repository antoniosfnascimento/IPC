"""Elevation enrichment for the routing graph.

OSM `incline` tags are sparse in most cities (especially Vila Real, where
they cover <5% of edges). To compute reliable slope penalties we query a
public Digital Elevation Model and derive grade per edge from the node
elevations.

Public endpoint: https://www.opentopodata.org (free, no API key, batches of
up to 100 points per request, 1 req/s). Dataset `eudem25m` provides 25 m
resolution over Europe; we fall back to the global `srtm30m` dataset for
coordinates outside Europe.
"""

import logging
import time
from typing import Iterable, List, Optional, Tuple

import requests

OPENTOPODATA_ENDPOINT = "https://api.opentopodata.org/v1"
DEFAULT_DATASET = "eudem25m"
FALLBACK_DATASET = "srtm30m"
BATCH_SIZE = 100
REQUEST_TIMEOUT = 15
INTER_BATCH_DELAY = 1.0

log = logging.getLogger(__name__)


class ElevationServiceError(RuntimeError):
    """Raised when the elevation API cannot be reached or returns an error."""


def _chunks(items: List, size: int) -> Iterable[List]:
    for i in range(0, len(items), size):
        yield items[i:i + size]


def _query_batch(coords: List[Tuple[float, float]], dataset: str) -> List[Optional[float]]:
    locations = "|".join(f"{lat:.6f},{lon:.6f}" for lat, lon in coords)
    url = f"{OPENTOPODATA_ENDPOINT}/{dataset}"
    response = requests.get(url, params={"locations": locations}, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    payload = response.json()
    if payload.get("status") != "OK":
        raise ElevationServiceError(payload.get("error", "Unknown elevation API error"))
    return [result.get("elevation") for result in payload.get("results", [])]


def fetch_elevations(coords: List[Tuple[float, float]], dataset: str = DEFAULT_DATASET) -> List[Optional[float]]:
    """Fetch elevation (metres above sea level) for a list of (lat, lon) pairs."""
    if not coords:
        return []

    elevations: List[Optional[float]] = []
    for batch_index, batch in enumerate(_chunks(coords, BATCH_SIZE)):
        if batch_index > 0:
            time.sleep(INTER_BATCH_DELAY)
        try:
            elevations.extend(_query_batch(batch, dataset))
        except (requests.RequestException, ElevationServiceError) as exc:
            if dataset != FALLBACK_DATASET:
                log.warning("Falling back to %s after error on %s: %s", FALLBACK_DATASET, dataset, exc)
                elevations.extend(_query_batch(batch, FALLBACK_DATASET))
            else:
                raise ElevationServiceError(str(exc)) from exc
    return elevations


MAX_REALISTIC_GRADE = 0.25
MIN_GRADE_SEGMENT_METERS = 20.0


def annotate_graph_with_elevation(graph, dataset: str = DEFAULT_DATASET) -> int:
    """Annotate every node with `elevation` and every edge with `grade`/`grade_abs`.

    Returns the number of nodes that were successfully populated. Edges with
    missing elevation on either endpoint keep `grade = 0.0` to stay safe.

    The grade is capped at MAX_REALISTIC_GRADE (25%) because the underlying DEM
    has ~25 m resolution. Short edges (< MIN_GRADE_SEGMENT_METERS) are
    smoothed against the longer chain they belong to so a single noisy
    elevation sample does not poison the routing peak-slope summary.
    """
    node_ids = list(graph.nodes())
    coords = [(graph.nodes[n]["y"], graph.nodes[n]["x"]) for n in node_ids]
    log.info("Requesting elevation for %d nodes via OpenTopoData (%s)...", len(node_ids), dataset)
    elevations = fetch_elevations(coords, dataset=dataset)

    populated = 0
    for node_id, elev in zip(node_ids, elevations):
        if elev is None:
            continue
        graph.nodes[node_id]["elevation"] = float(elev)
        populated += 1

    for u, v, k, data in graph.edges(keys=True, data=True):
        elev_u = graph.nodes[u].get("elevation")
        elev_v = graph.nodes[v].get("elevation")
        length = data.get("length", 0.0)
        if elev_u is None or elev_v is None or not length or length <= 0:
            data["grade"] = 0.0
            data["grade_abs"] = 0.0
            continue
        rise = float(elev_v) - float(elev_u)
        raw_grade = rise / float(length)
        damping = min(1.0, float(length) / MIN_GRADE_SEGMENT_METERS) if length < MIN_GRADE_SEGMENT_METERS else 1.0
        grade = max(-MAX_REALISTIC_GRADE, min(MAX_REALISTIC_GRADE, raw_grade * damping))
        data["grade"] = grade
        data["grade_abs"] = abs(grade)

    log.info("Elevation annotation complete: %d/%d nodes populated.", populated, len(node_ids))
    return populated
