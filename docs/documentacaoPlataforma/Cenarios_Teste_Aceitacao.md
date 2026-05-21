# Acceptance Test Scenarios for Routing Business Rules (QA)

To verify that the mathematical engine of CityFlow and the penalty metrics (data dictionary and mathematical logic) work correctly in a real context, the QA team must validate the algorithm against the following five edge scenarios.

These tests prove the system delivers on its MVP value proposition: prioritising *physical viability* over *distance*.

---

## Scenario 1 — Resistance and high slope
**Profile:** Manual wheelchair user (strong motor restriction, low cardiac tolerance).
**Goal:** Travel from "Câmara Municipal de Vila Real" to the "Bus Terminal".
**Active variables:** `max_incline: 0.08` (8%). `avoid_stairs: True`.
**Acceptance criteria:**
1. The algorithm **cannot** pick streets steeper than 8%, even if they are the shortest straight line.
2. The generated path must zig-zag along the contour lines (transversal streets) to neutralise the terrain elevation, showcasing the ×15 multiplier.
3. *Pass criterion:* The total length (e.g. 2.1 km) must be visibly larger and provably viable compared to the straight-line distance (e.g. 800 m).

---

## Scenario 2 — Dead end and strict surface filter
**Profile:** Senior with reduced mobility (uses a walker).
**Goal:** Cross the historic cobblestone part of the city to reach the Cathedral.
**Active variables:** `surface_preference: ['paved', 'asphalt']`, explicitly excluding `cobblestone`. `max_incline: 0.12`.
**Acceptance criteria:**
1. The system must prefer smooth asphalt. If the only direct access to the cathedral is mostly cobblestone, the route must avoid that artery.
2. The route should detour around squares with Portuguese cobblestone (×3.5 penalty) as much as possible.
3. *Fallback:* If the only streets within the last 100 m before the cathedral are cobblestone, the system must not crash (HTTP 424); instead, it returns a route minimising cobblestone exposure and shows an alert: "Bumpy floor on the final stretch".

---

## Scenario 3 — Low-vision slope tolerance
**Profile:** Low-vision user (uses a tactile cane).
**Goal:** Move from the student residences to the southern limit of the UTAD campus (very hilly terrain).
**Active variables:** `max_incline: 0.20` (20%). Crosswalk penalty active.
**Acceptance criteria:**
1. The route must not contour blocks just because of elevation. With a 20% tolerance, the path should look essentially like a straight line.
2. The system must detect dangerous roundabouts (fast traffic, crosswalks without electronic signalling or tactile islands) and re-route through underpasses or crosswalks with audio signals (×10 penalty), ignoring distance.

---

## Scenario 4 — Real-time crowdsourcing
**Profile:** Any user with physical limits.
**Goal:** Daily morning commute (A → B) that crosses a single narrow bridge.
**Active variables:** `POST /api/v1/report-barrier` was triggered. A `is_blocked: True` barrier was placed 30 min before exactly on the bridge.
**Acceptance criteria:**
1. The algorithm reaches the section where `is_blocked = True` was injected into RAM and the 99999 penalty kicks in.
2. The algorithm closes the lane and re-routes the user before the obstacle.
3. If the lane is the only land entrance (creating a true isolated node), the API must reply with a semantic business error ("Path crossed by obstacle. No alternative routes until removal.") rather than retrying empty calls in a loop.

---

## Scenario 5 — Robustness against missing tags
**Profile:** Double stroller or motorised wheelchair (extra-wide load).
**Goal:** Walk between two homes in a peripheral residential area.
**Active variables:** `min_width: 1.25 m`.
**Acceptance criteria:**
1. The engine finds residential edges that lack the OSM `width` tag.
2. `FeatureSanitizer` kicks in and prevents a 500 (Pydantic ValueError) or a Python crash on `None < 1.25`.
3. The default conservative width (1.0 m) means 1.0 < 1.25 ⇒ the unmapped edge is rejected for safety, avoiding the user getting stuck against narrow walls.
