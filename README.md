# Apex Retail Store Intelligence Platform

This repository contains the end-to-end Store Intelligence Platform built for Apex Retail's physical stores, combining a Computer Vision detection pipeline, a robust FastAPI REST API, SQLite storage, and a stunning live glassmorphic web dashboard.

---

## 🚀 5-Command Quickstart Guide

Start the platform, run the pipeline, verify tests, and load the dashboard in exactly 5 commands:

### Command 1: Start the REST API & Storage Server
Starts the containerized FastAPI server, initializes the database, and seeds the POS transactions in one step:
```bash
docker compose up --build
```

### Command 2: Run the Vision & Detection Pipeline
Runs the detection pipeline which processes camera feeds and streams structured events into the API:
```bash
./store-intelligence/pipeline/run.sh
```

### Command 3: Run Automated Test Suite
Executes all 7 high-coverage unit and integration tests inside the running API container:
```bash
docker compose exec api pytest store-intelligence/tests/ -v
```

### Command 4: Check API Health Endpoint
Verifies service status, database connectivity, and camera feed stale checks:
```bash
curl http://localhost:8000/health
```

### Command 5: Open the Live Glassmorphic Dashboard
Open your browser and navigate to the interactive visual intelligence dashboard:
```bash
open http://localhost:8000/dashboard
```

---

## 🎨 Platform Features

* **Glassmorphic Live Dashboard**: A modern, high-end visual dashboard served directly from the backend. Features a real-time store layout heatmap (Skincare vs Makeup shelves vs Cash Counter), conversion funnel percentages, metrics cards, and scrollable operational alert notifications.
* **Simulated Replay Control Center**: Includes an interactive button directly on the Web UI to stream simulated camera events and watch the metrics, heatmaps, and funnel charts update dynamically in real-time!
* **High-Coverage Test Harness**: Includes 7 unit and integration tests validating event schemas, idempotency (duplicate check safety), staff exclusion logic, and mathematical consistency across conversion funnels.
* **Structured JSON Logging**: Custom middleware automatically tracks every request's `trace_id`, `store_id`, `endpoint`, HTTP `status_code`, and execution latency in milliseconds for production observability.

---

## 📂 Repository Structure

* `/store-intelligence/pipeline/`: Contains the vision tracking core:
  * `detect.py`: The main video loop with dual cores (YOLOv8 + pre-calibrated Simulated CV fallback).
  * `tracker.py`: Centroid tracker, Re-ID handoffs, and staff uniform classification.
  * `emit.py`: Event schema validation and batch POST requests.
  * `run.sh`: Unzips CCTV clips and runs the pipeline.
* `/store-intelligence/app/`: The REST API backend:
  * `main.py`: FastAPI server configuration, structured logging middleware, and routing.
  * `database.py`: SQLite schemas and POS data seeding.
  * `metrics.py` / `funnel.py` / `heatmap.py` / `anomalies.py` / `health.py`: Analytic endpoints logic.
  * `templates/index.html`: Stunning frontend dashboard interface.
* `/store-intelligence/tests/`: Diagnostic tests with required AI prompt headers.
* `/store-intelligence/docs/`: Architectural design and choice documentations:
  * `DESIGN.md`: High-level system layout and AI-assisted decisions.
  * `CHOICES.md`: Trade-offs and rationale behind model, database, and API selections.
