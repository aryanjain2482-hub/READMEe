# RouteWise — Intelligent Multi-Agent Route Optimization

Web Forge 2026 · PS 01 · Team: Aryan Jain (leader), Lakshya Yadav, Pallavi Garg

RouteWise assigns delivery orders to several agents and builds efficient routes while respecting
**vehicle capacity, delivery time windows, order priority and fair workload**. When an order is
**added, cancelled, delayed or reassigned** (or an agent goes off duty) the whole plan is
**re-optimized instantly**, and a dashboard shows the measurable improvement over a naive baseline.

## Features
- Interactive map (Leaflet + OpenStreetMap), one colour per agent, numbered stops, ETA popups
- Constraint-aware allocation: capacity, time windows (early = wait, late = penalised), priority (urgent orders are protected), workload balance
- Dynamic events: add order (click on map), cancel/restore, +30 min delay, manual reassign (locks an order to an agent), agent off duty
- Baseline vs RouteWise comparison (distance, late deliveries, late minutes, urgent orders late, workload gap)
- Re-optimization log: how many orders moved agent, solve time, before/after metrics
- Friendly cartoon UI: original animal-courier mascots (one per agent, bandana = route colour), a talking helper robot "Rooty", comic-style cards, and synthesized sound effects with a mute button (all artwork and sounds are original)
- Real road distances from OSRM, with automatic fallback to straight-line × 1.3 if offline

## Tech
React + TypeScript + Tailwind + Leaflet · FastAPI (Python) · Google OR-Tools (VRPTW) ·
pure-Python fallback optimizer (cheapest insertion + local search) used if OR-Tools is missing.

## Run it

### 1. Backend (terminal 1)
```bash
cd backend
python -m venv .venv
# Windows:  .venv\Scripts\activate        Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
Check: http://localhost:8000/api/health  (shows `"ortools": true` when OR-Tools is active)
API docs: http://localhost:8000/docs

### 2. Frontend (terminal 2)
```bash
cd frontend
npm install
npm run dev
```
Open http://localhost:5173

### 3. Tests
```bash
cd backend
set USE_OSRM=0        # Windows (cmd).  Mac/Linux: export USE_OSRM=0
pytest -q
```

## How the optimizer works (for the viva / judges)
- **Problem:** Vehicle Routing Problem with Time Windows (VRPTW) + capacity + priorities + balance.
- **One cost function** (`backend/app/objective.py`): distance + late-minutes × priority weight (urgent ×5, high ×2.5) + workload-balance penalty + big penalty for dropping an order.
- **Baseline** (`baseline.py`): hand orders out round-robin in arrival order, ignoring location and deadlines.
- **RouteWise** (`solver_ortools.py`): OR-Tools with Capacity, Time and Count dimensions, soft deadlines, guided local search. `solver_heuristic.py` is the dependency-free fallback.
- **Fair comparison:** both plans are scored by the same simulator (`evaluate.py`).
- **Re-optimization:** every event updates the order data and re-solves from scratch in milliseconds–seconds (`engine.py`).

## Folder map
```
backend/app/   models, geo (OSRM), evaluate, objective, baseline, solver_ortools, solver_heuristic, engine, main (API), sample_data
backend/tests/ engine tests
frontend/src/  App, api, types, mascots, sfx, index.css, components/ (MapView, Comparison, AgentsPanel, OrdersPanel, AddOrderForm, EventLog, Rooty)
```

## Limitations (be honest in the presentation)
- State is in memory (resets when the server restarts); PostgreSQL was left out to fit the 12-hour limit.
- Routes on the map are straight lines between stops (the distances/times used are road-based when OSRM is reachable).
- Re-optimization re-solves the whole plan, so several orders can change agent after one event.
- Demo coordinates for Indore areas are approximate.
