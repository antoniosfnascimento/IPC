# Data Dictionary: User Profiles and Physical Constraints

This table specifies the *hard constraints* (mathematical and boolean constants based on universal accessibility manuals) that the geospatial engine applies to every edge of the OSM graph depending on the chosen profile. These parameters tune the Bellman-Ford penalty heuristic.

| User profile | Base limitation | Max slope (`max_incline`) | Min width (`min_width`) | Stairs (`avoid_stairs`) | Preferred surfaces (`surface_preference`) | Effort multiplier | Technical justification |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Wheelchair** | Motor / wheeled | 8% (0.08) | 1.20 m | `True` | `paved`, `asphalt`, `concrete`, `paving_stones` | ×15 on slopes > 5% | W3C ramp guideline and mandatory avoidance of loose ground (`gravel`, `dirt`) due to friction. |
| **Reduced mobility** (walker/crutches) | Instability / effort | 10% (0.10) | 0.90 m | `True` | `paved`, `asphalt`, `concrete`, `compacted` | ×10 on slopes > 8% | Lower tolerance to distance, but can fit through narrower paths than a wheelchair. |
| **Senior** | Fatigue / cardiac | 12% (0.12) | 0.80 m | `False` (but avoid if > 5 steps) | `paved`, `asphalt`, `concrete` | ×20 on stairs, ×5 on long climbs | Greater focus on physical exhaustion on climbs than on path width. Stairs are possible but heavily penalised. |
| **Stroller** | Small wheels / vibration | 15% (0.15) | 0.90 m | `True` | `paved`, `asphalt`, `concrete` | ×5 on potholes (`cobblestone`) | Lower cardiac restriction than "Senior", but strong aversion to vibrating floors (the cobblestone of Vila Real) for the baby's comfort. |
| **Low vision** | Tactile references | 20% (0.20) | 0.90 m | `False` | Any | N/A | Focus is not on effort but on avoiding non-levelled lowered curbs (or using tactile paving). |
| **Distance-focused** (standard) | None | 30% (0.30) | 0.50 m | `False` | Any | ×1 | Uses pure shortest-distance Bellman-Ford with no hardware / effort penalty. |

**Engineering notes (`router.py`):**
*   **Slope (`incline`):** In OSM, the `incline` value is often stored with the downhill sign (`-5%`) or uphill sign (`5%`) depending on the edge direction. The engine uses `abs()` so the fatigue constraint applies regardless of direction. Since the OSM `incline` tag is sparse in Vila Real, the engine falls back to a per-edge grade computed from the OpenTopoData elevation API (EU-DEM 25 m dataset).
*   **Width (`width`):** Streets in Portugal (especially historical centres such as Vila Real) often *do not* have the `width` tag set in OSM. Filtering too strictly breaks the graph and yields HTTP 424. The fallback is to assume 0.5 m for missing values and rely on the multiplier to push routing towards taggeable streets.
