# Multi-City Viability Report

## Why this report exists
During the project review the supervising lecturer challenged the assumption that a larger city (Paris, New York) automatically ships more accessibility-relevant OpenStreetMap data than Vila Real. The doubt is legitimate — population alone is not a proxy for mapping density.

This document presents the **measured** OSM tag density used by the CityFlow routing engine on a 1.5 km radius around the city centre of each candidate, so that the choice of supported cities is justified by data rather than intuition.

All numbers were collected on 21 May 2026 against the live Overpass API through OSMnx 2.1.0 (`network_type='walk'`, `radius=1500m`). They are reproducible by running the snippet at the bottom of this document.

## Method
For each candidate city centre we downloaded the walkable graph and counted, per edge, how often each accessibility-relevant tag is present:

* **`surface`** — feeds the cobblestone/paving penalty (×3.5).
* **`smoothness`** — wheelchair-grade comfort rating (`excellent` → `very_bad`).
* **`incline`** — explicit slope tag (already complemented by our EU-DEM enrichment).
* **`width`** — pedestrian width constraint.
* **`wheelchair`** — explicit accessibility tag.
* **`tactile_paving`** — guidance for low-vision users.
* **`highway=steps`** — hard barrier for wheelchairs / strollers.

Two centres are reported:
* **Vila Real** — Avenida Carvalho Araújo, the historic axis already used by the MVP (lat 41.2960, lon -7.7460).
* **Paris** — Châtelet–Les Halles, in the centre of the city (lat 48.8584, lon 2.3470). Châtelet was picked because it sits at the intersection of medieval, Haussmannian and contemporary urban fabrics, so it touches every surface family in our penalty table.

> A first iteration also benchmarked Times Square (New York). The result is summarised at the end of the document — short version: NYC ships ~2.2× more edges than Vila Real, but the surface vocabulary is dominated by `concrete`+`asphalt` (i.e. uniform), so the surface and slope filters would respond less visibly than they do in Paris.

## Results

| Metric (1.5 km radius) | Vila Real | Paris (Châtelet) | Ratio Paris ÷ Vila Real |
| :--- | ---: | ---: | ---: |
| Edges in walk graph | 7 366 | 28 756 | **3.9×** |
| Nodes | 2 811 | 10 039 | 3.6× |
| Edges with `surface` | 5 372 (72.9 %) | 22 870 (79.5 %) | 4.3× |
| Edges with `smoothness` | 46 (0.6 %) | 9 072 (31.5 %) | **197×** |
| Edges with `incline` | 84 (1.1 %) | 1 404 (4.9 %) | 16.7× |
| Edges with `width` | 176 (2.4 %) | 122 (0.4 %) | 0.7× |
| Edges with `wheelchair` | 0 | 36 | n/a |
| Edges with `tactile_paving` | 60 | 1 162 | 19.4× |
| `highway=steps` | 70 | 72 | 1.0× |
| `highway=footway` | 1 492 | 23 784 | 15.9× |

### Surface vocabulary (counts)

| Surface | Vila Real | Paris |
| :--- | ---: | ---: |
| `asphalt` | 3 445 | 12 908 |
| `paving_stones` | 457 | 6 949 |
| `sett` | 992 | 1 234 |
| `concrete` | 220 | 436 |
| `compacted` | 0 | 809 |
| `fine_gravel` | 0 | 183 |
| `gravel` | 0 | 95 |
| `unhewn_cobblestone` | 38 | 0 |
| `ground` | 124 | 0 |
| `unpaved` / `dirt` / `wood` | 50 | 0 |
| `stone` / `concrete:plates` / `metal` | 10 | 182 |

### Smoothness vocabulary (counts)

| Smoothness | Vila Real | Paris |
| :--- | ---: | ---: |
| `excellent` | 10 | 1 672 |
| `good` | 18 | 6 490 |
| `intermediate` | 18 | 860 |
| `bad` | 0 | 46 |
| `very_bad` | 0 | 4 |

## Interpretation

### What surprises (and what doesn't)
1. **Vila Real is far from empty.** 72.9 % of its walk edges already carry a `surface` tag. The "the API has no data for Vila Real" intuition is incorrect; the city has been mapped at a respectable level of detail, especially around the historic centre.
2. **What Vila Real lacks is the *gradient* signals.** `incline` covers only 1.1 % of edges, and `smoothness` only 0.6 %. This is the reason the original MVP reported steep climbs as 0 % — not because Vila Real is missing from OSM, but because slope tagging is sparse there. We addressed that by adding the EU-DEM 25 m elevation enrichment on the backend.
3. **Paris is in a different league only on the *accessibility* axis.** It is not "more mapped overall" — it has a comparable percentage of `surface` tags (79.5 % vs 72.9 %). What Paris has that is genuinely rare elsewhere is the `smoothness` tag, present on 31.5 % of edges. That is the artefact of a deliberate accessibility-tagging campaign run by Wikimédia France and the city of Paris ahead of the 2024 Olympic and Paralympic Games. The same applies to `wheelchair` (36 edges) and `tactile_paving` (1 162 edges) — these are *campaign-driven* coverage, not population-driven.
4. **`width` is sparse everywhere.** Vila Real (2.4 %) actually beats Paris (0.4 %) on this tag. The OSMnx fallback in `sanitizer.py` (defensive 0.5 m default) is therefore relevant for both cities.

### Net effect on CityFlow demos
Each profile filter operates on a different tag:

| Filter | Wins in Vila Real | Wins in Paris |
| :--- | :--- | :--- |
| Avoid stairs | Comparable | Comparable |
| Surface preference | Has cobblestone / sett rich vocabulary | Has the same plus `compacted` / `fine_gravel` (parks) |
| Slope (max_incline) | Driven by EU-DEM (raw OSM tag almost absent) | Driven by EU-DEM **and** native OSM `incline` |
| Width | Defensive default kicks in (both cities) | Defensive default kicks in (both cities) |

Because Paris has 16.7× more `incline` tags and 197× more `smoothness` tags, every slider movement in Paris produces a more visible change of route than in Vila Real. Vila Real is **viable** but a Paris demo is **dramatic**. That justifies adding Paris as a second supported city rather than replacing Vila Real.

## Decision

CityFlow supports two cities side-by-side:

1. **Vila Real** (default) — the academic baseline. The MVP was originally designed around the historic centre and the user research (Personas João, Maria, Ricardo) is local. The recently added EU-DEM enrichment closes the slope gap.
2. **Paris (Châtelet)** — the showcase. Demonstrates the differentiated behaviour of every filter under data-rich conditions and lets the live demo trigger surface, smoothness and slope penalties on a single trip.

Both graphs are warmed on backend startup; the frontend offers a dropdown that switches the map view, the snap target and the routing target without reload. No claim is made that Paris is "objectively better mapped". The claim is narrower and supported by the numbers: **Paris ships more accessibility-specific tagging in the radius used by CityFlow, mostly thanks to a campaign-driven mapping effort that has no equivalent in Vila Real.**

## New York: why it was dropped
Times Square (New York) returned 16 312 edges (2.2× Vila Real, 0.6× Paris), `surface` coverage of 71.3 %, but the vocabulary is dominated by `concrete` (5 559) and `asphalt` (3 968) with very little variety. The slope filter would also be muted (Manhattan around 42nd street is essentially flat) and EU-DEM does not cover the United States, requiring a fallback to SRTM 30 m which is coarser. New York remained on the shortlist but, on this specific metric — *how visibly do the sliders change the route?* — it scored lower than Paris, so it is not part of the first multi-city release.

## Reproducing the numbers
```python
import osmnx as ox
from collections import Counter

ox.settings.useful_tags_way = list(set(list(ox.settings.useful_tags_way) + [
    "incline", "surface", "width", "smoothness", "wheelchair",
    "sidewalk", "tactile_paving",
]))

centers = {
    "Vila Real": (41.2960, -7.7460),
    "Paris":     (48.8584,  2.3470),
}

for label, (lat, lon) in centers.items():
    G = ox.graph_from_point((lat, lon), dist=1500, network_type="walk")
    edges = list(G.edges(keys=True, data=True))
    total = len(edges)
    def pct(tag): return sum(1 for *_, d in edges if d.get(tag)) / total * 100
    print(f"{label}: {total} edges, surface={pct('surface'):.1f}%, "
          f"smoothness={pct('smoothness'):.1f}%, incline={pct('incline'):.1f}%")
```
