"""Enriquecimento de elevação para o grafo de rotas.

As tags OSM `incline` são esparsas na maioria das cidades (em Vila Real
cobrem <5 % das arestas). Para calcular penalizações de declive fiáveis,
consultamos um Modelo Digital de Elevação público e derivamos o declive
por aresta a partir das elevações dos nós.

Endpoint público: https://www.opentopodata.org (gratuito, sem chave de API,
lotes até 100 pontos por pedido, 1 req/s). O conjunto `eudem25m` fornece
resolução de 25 m sobre a Europa; recorremos ao conjunto global `srtm30m`
em fallback para coordenadas fora da Europa.

A elevação por nó é guardada em disco em `backend/data/elevation_cache/`,
para que o (lento) pedido à API seja pago apenas uma vez por cidade.
"""

import json
import logging
import os
import time
from typing import Iterable, List, Optional, Tuple

import requests

OPENTOPODATA_ENDPOINT = "https://api.opentopodata.org/v1"
DEFAULT_DATASET = "eudem25m"
FALLBACK_DATASET = "srtm30m"
BATCH_SIZE = 100
REQUEST_TIMEOUT = 15
INTER_BATCH_DELAY = 1.2  # O free tier do OpenTopoData limita a ~1 req/s; ficamos com margem.
MAX_RATE_LIMIT_RETRIES = 4

log = logging.getLogger(__name__)


class ElevationServiceError(RuntimeError):
    """Lançado quando a API de elevação não consegue responder ou devolve erro."""


def _chunks(items: List, size: int) -> Iterable[List]:
    for i in range(0, len(items), size):
        yield items[i:i + size]


def _query_batch(coords: List[Tuple[float, float]], dataset: str) -> List[Optional[float]]:
    locations = "|".join(f"{lat:.6f},{lon:.6f}" for lat, lon in coords)
    url = f"{OPENTOPODATA_ENDPOINT}/{dataset}"
    backoff = 2.0
    for attempt in range(MAX_RATE_LIMIT_RETRIES):
        response = requests.get(url, params={"locations": locations}, timeout=REQUEST_TIMEOUT)
        if response.status_code == 429:
            log.warning(
                "OpenTopoData devolveu rate-limit (HTTP 429). A dormir %.1fs (tentativa %d/%d).",
                backoff, attempt + 1, MAX_RATE_LIMIT_RETRIES,
            )
            time.sleep(backoff)
            backoff = min(backoff * 2, 20.0)
            continue
        response.raise_for_status()
        payload = response.json()
        if payload.get("status") != "OK":
            raise ElevationServiceError(payload.get("error", "Erro desconhecido da API de elevação"))
        return [result.get("elevation") for result in payload.get("results", [])]
    raise ElevationServiceError("O rate-limit do OpenTopoData continuou a rejeitar o pedido.")


def fetch_elevations(coords: List[Tuple[float, float]], dataset: str = DEFAULT_DATASET) -> List[Optional[float]]:
    """Obtém a elevação (metros acima do nível do mar) para uma lista de pares (lat, lon)."""
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
                log.warning("A recorrer a %s após erro em %s: %s", FALLBACK_DATASET, dataset, exc)
                elevations.extend(_query_batch(batch, FALLBACK_DATASET))
            else:
                raise ElevationServiceError(str(exc)) from exc
    return elevations


MAX_REALISTIC_GRADE = 0.25
MIN_GRADE_SEGMENT_METERS = 20.0


_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ELEVATION_CACHE_DIR = os.path.join(_BACKEND_DIR, "data", "elevation_cache")
os.makedirs(ELEVATION_CACHE_DIR, exist_ok=True)


def _cache_path(cache_key: Optional[str]) -> Optional[str]:
    if not cache_key:
        return None
    safe = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in cache_key)
    return os.path.join(ELEVATION_CACHE_DIR, f"{safe}.json")


def _load_cache(cache_key: Optional[str]) -> dict:
    path = _cache_path(cache_key)
    if not path or not os.path.exists(path):
        return {}
    try:
        with open(path, "r") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        log.warning("A cache de elevação em %s não é legível; a reconstruir.", path)
        return {}


def _save_cache(cache_key: Optional[str], cache: dict) -> None:
    path = _cache_path(cache_key)
    if not path:
        return
    try:
        with open(path, "w") as fh:
            json.dump(cache, fh)
    except OSError as exc:
        log.warning("Não foi possível persistir a cache de elevação em %s: %s", path, exc)


def annotate_graph_with_elevation(graph, dataset: str = DEFAULT_DATASET, cache_key: Optional[str] = None) -> int:
    """Anota cada nó com `elevation` e cada aresta com `grade`/`grade_abs`.

    Devolve o número de nós populados com sucesso. Arestas com elevação em
    falta nos extremos mantêm `grade = 0.0` por segurança.

    O declive é limitado a MAX_REALISTIC_GRADE (25 %) porque o DEM
    subjacente tem ~25 m de resolução. Arestas curtas (< MIN_GRADE_SEGMENT_METERS)
    são suavizadas, para que uma amostra de elevação ruidosa não envenene
    o resumo do declive máximo da rota.
    """
    node_ids = list(graph.nodes())
    cache = _load_cache(cache_key)
    missing_ids = [n for n in node_ids if str(n) not in cache]
    if missing_ids:
        coords = [(graph.nodes[n]["y"], graph.nodes[n]["x"]) for n in missing_ids]
        log.info(
            "A pedir elevação para %d nós via OpenTopoData (%s)... (cache hits: %d)",
            len(missing_ids), dataset, len(node_ids) - len(missing_ids),
        )
        try:
            elevations = fetch_elevations(coords, dataset=dataset)
            for node_id, elev in zip(missing_ids, elevations):
                if elev is None:
                    continue
                cache[str(node_id)] = float(elev)
            _save_cache(cache_key, cache)
        except (ElevationServiceError, requests.RequestException) as exc:
            # Persiste o que já temos para o próximo arranque retomar mais rápido,
            # e deixa o caller decidir o que fazer (o router trata como aviso e
            # as penalizações de declive recaem na tag OSM `incline`).
            _save_cache(cache_key, cache)
            raise ElevationServiceError(str(exc)) from exc
    else:
        log.info("Todas as %d elevações de nó vieram da cache em disco.", len(node_ids))

    populated = 0
    for node_id in node_ids:
        elev = cache.get(str(node_id))
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

    log.info("Anotação de elevação concluída: %d/%d nós populados.", populated, len(node_ids))
    return populated
