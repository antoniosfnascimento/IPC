# Penalty Heuristics and Mathematical Logic (Routing Engine)

This document specifies the exact numeric weights that the routing algorithm assigns to graph edges (streets) to intentionally avoid non-accessible paths, computing the *effective cost* of every road.

The central formula for the weighting engine is:
`Directional cost (W) = Physical distance (m) × Σ Penalties`

---

## 1. Penalty table by surface type

Based on the OSM `surface` attribute. Values > 1.0 represent additional effort / discomfort for wheelchairs and walkers.

| Surface type (OSM tag) | Floor description | Penalty point | Rationale |
| :--- | :--- | :--- | :--- |
| `paved`, `asphalt`, `concrete` | Smooth consolidated pavement | **1.0 (neutral)** | Ideal floor. No extra friction. A 100 m street costs 100 m. |
| `paving_stones`, `sett` | Consolidated paving stones | **1.5** | Adds 50% cost. Some vibration and push effort, but perfectly viable and inherent to historical centres like Vila Real. |
| `cobblestone` | Portuguese cobblestone (irregular) | **3.5** | High vibration, risk of trapping wheelchair front castors and slipping crutches when wet. A 100 m street now costs 350 m, pushing the algorithm towards a longer smooth detour. |
| `compacted`, `fine_gravel` | Compacted dirt / fine gravel | **5.0** | High traction effort. Wheels sink slightly. Avoid at almost any cost. |
| `gravel`, `dirt`, `sand` | Loose gravel, dirt, sand | **20.0** | Practically impassable for any rolling mobility aid. Acts almost as a barrier. |

---

## 2. Barrier and static penalties

Applied across the board when explicit obstacles exist on the road.

| Barrier type (OSM / API) | Affected profile | Penalty point | Rationale |
| :--- | :--- | :--- | :--- |
| `highway=steps` (stairs) | Wheelchair, stroller | **10000.0 (infinite / cut)** | Impassable architectural barrier (hard constraint). The weight makes it impossible for the algorithm to select this path regardless of the alternative distance. |
| Crosswalk without audio signal | Blind / low-vision | **10.0** | Severe risk. Pushes blind users towards signalled intersections or continuous protected pavements — even ten times longer routes are accepted for safety. |
| `is_blocked=True` (crowdsourcing) | All | **99999.0 (temporal cut)** | Feedback submitted by users (works, parked cars on the pavement). Temporarily cuts the edge. |

---

## 3. The math behind the `15.0` slope multiplier

The theoretical justification in civil engineering and biomechanics for the `15.0` constant in the slope penalty function is based on the *law of excess work* and the exhaustion of human propulsion force on inclined planes.

### Why not `2.0` or `5.0`? (Coefficient study)
If we set a street whose slope exceeds the wheelchair limit (e.g. > 8%) to a mild penalty (e.g. `2.0`), the algorithm would read a 100 m steep climb as a "200 m" path.
*   **The problem with a low weight:** if the alternative (the ideal flat street) requires a 300 m detour, the algorithm would still pick the steep street (200 cost vs 300 cost). That would **force the user up a hill they cannot sustain by hand**, jeopardising their health or causing a backward wheelchair crash — a fatal risk.

### The exponential effort function
In assisted human locomotion, the energy required to fight gravity on a surface above 5% follows an asymptotic curve. Arm muscle fatigue grows exponentially.
*   An 8% climb is tolerable for very short distances.
*   A 12% ramp without a handrail is often impassable regardless of distance.

**Setting Penalty = 15.0** tells the graph: *"Climbing this 100 m hill costs you the equivalent of a 1.5 km flat trip."*

That high cost forces Bellman-Ford to "panic" and search for dozens of alternatives, preferring a 1.2 km zig-zag along flat avenues rather than a straight bumpy climb up the UTAD hill. This coefficient was tested as the *golden ratio* for micro-routing — high enough to redirect, low enough to keep the graph connected.

---

## 4. Real elevation enrichment (replaces sparse OSM `incline` tags)

OSM `incline` data covers less than 5% of the streets in Vila Real. Without a real source of slope, every filter degenerates to 0%.

On startup the engine queries **OpenTopoData** (free, no API key, EU-DEM dataset at 25 m resolution) for each graph node and stores the elevation. Every edge derives its grade as `(elev_v − elev_u) / length`.

Two corrections are applied:
1. **Cap at 25%.** The DEM has 25 m resolution; differences over very short edges (< 20 m) tend to be noisy. The grade is clamped to [-0.25, 0.25].
2. **Smoothing on short edges.** When an edge is shorter than the DEM resolution, the grade is multiplied by `length / 20`, reducing noise from a single elevation sample.

The router prefers the elevation-derived grade and only falls back to the OSM `incline` tag when elevation enrichment fails.
