# CityFlow Vila Real — Inclusive Civic Navigation

## Overview
Assisted-mobility routing for vulnerable urban profiles (Seniors, Wheelchair users) in Vila Real. The engine rewrites the classic "shortest path" into a "most viable path" by injecting accessibility penalties on every edge of the OpenStreetMap graph.

## Tech stack
- **FastAPI** (Python)
- **React** (Vite + Tailwind v4)
- **OSMnx** + **NetworkX** for graph processing
- **Leaflet** for the map UI
- **OpenTopoData** (free Digital Elevation Model) for real-world slope enrichment

## How the routing math works
The engine runs Bellman-Ford over the OSM walk network. Every edge weight $W_e$ multiplies the segment length by an accessibility penalty:

$$W_e = \text{length} \times \text{total penalty (slope + surface + stairs + width)}$$

Slope is the most important input — and the project's biggest hidden risk. OSM `incline` tags cover less than 5% of Vila Real's streets, so the backend reaches out to the **OpenTopoData EU-DEM** dataset on startup to compute a real per-edge grade from node elevations. This is how the climb to UTAD now shows up correctly instead of being silently flattened to 0%.

## Features
- **Coverage bounding box** — keeps the routing graph small and fast.
- **Real slope analysis** — elevation-derived grade is used to penalise steep edges, with a softer "approaching limit" multiplier in addition to the hard 15× cut.
- **Walkable snap-point** — A/B points are projected onto the nearest pedestrian-friendly edge (up to 250 m). Motorways, trunk roads and untaggable terrain are excluded.
- **Kinematic time estimate** — walking speed is adjusted for senior/wheelchair pacing.

## Installation

### Backend (Python API)
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

First boot will fetch ~2-3k elevation points from OpenTopoData (free, no key) — this takes ~30 s once. OSMnx caches the graph locally; subsequent runs are instantaneous.

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
