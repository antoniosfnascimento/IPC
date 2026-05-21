# CityFlow — Inclusive Civic Navigation

## Overview
Assisted-mobility routing for vulnerable urban profiles (Seniors, Wheelchair users). The engine rewrites the classic "shortest path" into a "most viable path" by injecting accessibility penalties on every edge of the OpenStreetMap graph.

## Supported cities
The MVP ships with two cities loaded side-by-side. The frontend lets the user switch between them; both graphs are warmed at backend startup.

| City | Centre (lat, lon) | Radius | Why it is supported |
| :--- | :--- | :--- | :--- |
| **Vila Real** (default) | 41.296, -7.746 | 1.5 km | Academic baseline tied to the UTAD-driven user research (Personas João, Maria, Ricardo). |
| **Paris (Châtelet)**     | 48.8584, 2.347 | 1.5 km | Showcase: dense OSM data and 31.5% of edges tagged with `smoothness`, so every filter visibly steers the route. See `docs/documentacaoPlataforma/Multi_City_Viability_Report.md` for the comparative numbers. |

## Tech stack
- **FastAPI** (Python)
- **React** (Vite + Tailwind v4)
- **OSMnx** + **NetworkX** for graph processing
- **Leaflet** for the map UI
- **OpenTopoData** (free Digital Elevation Model) for real-world slope enrichment

## How the routing math works
The engine runs Bellman-Ford over the OSM walk network. Every edge weight $W_e$ multiplies the segment length by an accessibility penalty:

$$W_e = \text{length} \times \text{total penalty (slope + surface + stairs + width)}$$

Slope is the most important input — and the project's biggest hidden risk. Where OSM `incline` tags are sparse (in Vila Real they cover ~1 % of edges), the backend queries the **OpenTopoData EU-DEM** dataset on startup to compute a real per-edge grade from node elevations. This is how the climb to UTAD now shows up correctly instead of being silently flattened to 0 %.

## Features
- **Multi-city selector** — switch between Vila Real and Paris from the sidebar; the map, snap target and routing engine follow automatically.
- **Real slope analysis** — elevation-derived grade is used to penalise steep edges, with a softer "approaching limit" multiplier in addition to the hard 15× cut.
- **Walkable snap-point** — A/B points are projected onto the nearest pedestrian-friendly edge (up to 250 m). Motorways, trunk roads and untaggable terrain are excluded.
- **Kinematic time estimate** — walking speed is adjusted for senior/wheelchair pacing.
- **Coverage bounding box** — keeps the routing graph small (1.5 km radius) and the response time below ~1 s after the first boot.

## Installation

### Backend (Python API)
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

First boot will warm up both city graphs and fetch their elevation grids from OpenTopoData (free, no key) — count on ~1 minute total. OSMnx caches the graphs locally; subsequent runs are instantaneous.

### Frontend (React app)
With the backend running, in a new terminal:
```bash
cd frontend
npm install
npm run dev
```

## One-shot scripts
- macOS / Linux: `./start.sh` and `./stop.sh`
- Windows: `./start.ps1` and `./stop.ps1`
