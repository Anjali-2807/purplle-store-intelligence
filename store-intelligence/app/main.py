import os
import time
import uuid
import json
import logging
from fastapi import FastAPI, Request, Response, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any

from app.database import init_db, seed_pos_transactions
from app.models import (
    IngestResponse, StoreMetricsResponse, StoreFunnelResponse, 
    StoreHeatmapResponse, StoreAnomaliesResponse, HealthStatusResponse
)
from app.ingestion import ingest_events
from app.metrics import calculate_store_metrics
from app.funnel import calculate_store_funnel
from app.heatmap import calculate_store_heatmap
from app.anomalies import detect_store_anomalies
from app.health import calculate_service_health, track_ingest_activity

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("store_intelligence")

app = FastAPI(
    title="Apex Retail Store Intelligence API",
    description="Production-grade AI-powered store analytics and anomaly detection system.",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup DB Initialization
@app.on_event("startup")
def startup_event():
    init_db()
    # Seed default transactions
    csv_file = "/Users/anjalitiwari/Desktop/Purplle Tech Challenge/Brigade_Bangalore_10_April_26 (1)bc6219c.csv"
    if os.path.exists(csv_file):
        seed_pos_transactions(csv_file)
    else:
        # Check inside docker container path (e.g. /app/Brigade_Bangalore_10_April_26 (1)bc6219c.csv or in workspace)
        container_csv = "/app/Brigade_Bangalore_10_April_26 (1)bc6219c.csv"
        if os.path.exists(container_csv):
            seed_pos_transactions(container_csv)

# Mounting static files if the directories exist
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Middleware for Structured Logging
@app.middleware("http")
async def structured_logging_middleware(request: Request, call_next):
    trace_id = str(uuid.uuid4())
    request.state.trace_id = trace_id
    
    start_time = time.time()
    
    # Try to extract store_id from path parameters
    # Paths are typically /stores/{store_id}/metrics, etc.
    path_parts = request.url.path.strip("/").split("/")
    store_id = "N/A"
    if len(path_parts) >= 2 and path_parts[0] == "stores":
        store_id = path_parts[1]
        
    response = await call_next(request)
    
    latency_ms = (time.time() - start_time) * 1000.0
    
    # For ingest endpoint, count events in request body if possible
    event_count = 0
    if request.url.path == "/events/ingest" and request.method == "POST":
        try:
            # Note: Reading body in middleware can block or need caching.
            # For simplicity, we can set event_count in request state in the endpoint, and retrieve it here!
            event_count = getattr(request.state, "event_count", 0)
        except Exception:
            pass

    log_data = {
        "trace_id": trace_id,
        "store_id": store_id,
        "endpoint": request.url.path,
        "method": request.method,
        "latency_ms": round(latency_ms, 2),
        "event_count": event_count,
        "status_code": response.status_code
    }
    
    logger.info(json.dumps(log_data))
    response.headers["X-Trace-ID"] = trace_id
    return response

# Error handling mapping to prevent database connection failures showing raw stack traces
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    trace_id = getattr(request.state, "trace_id", "unknown")
    logger.error(f"Global exception caught. Trace ID: {trace_id}. Error: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred. Please contact the administrator.",
            "trace_id": trace_id
        }
    )

# Endpoints
@app.post("/events/ingest", response_model=IngestResponse)
async def post_events_ingest(events: List[Dict[str, Any]], request: Request):
    request.state.event_count = len(events)
    
    # Store Ingestion wallclock tracking
    stores_in_batch = set()
    for e in events:
        s_id = e.get("store_id")
        if s_id:
            stores_in_batch.add(s_id)
            
    for store in stores_in_batch:
        track_ingest_activity(store)
        
    result = ingest_events(events)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["errors"][0]["message"])
    return result

@app.get("/stores/{id}/metrics", response_model=StoreMetricsResponse)
def get_store_metrics(id: str):
    # Verify store_id is supported or has data
    res = calculate_store_metrics(id)
    return res

@app.get("/stores/{id}/funnel", response_model=StoreFunnelResponse)
def get_store_funnel(id: str):
    res = calculate_store_funnel(id)
    return res

@app.get("/stores/{id}/heatmap", response_model=StoreHeatmapResponse)
def get_store_heatmap(id: str):
    res = calculate_store_heatmap(id)
    return res

@app.get("/stores/{id}/anomalies", response_model=StoreAnomaliesResponse)
def get_store_anomalies(id: str):
    res = detect_store_anomalies(id)
    return res

@app.get("/health", response_model=HealthStatusResponse)
def get_health():
    res = calculate_service_health()
    if res["status"] == "DOWN":
        return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content=res)
    return res

@app.get("/")
def redirect_to_dashboard():
    return RedirectResponse(url="/dashboard")

@app.get("/dashboard", response_class=HTMLResponse)
def view_dashboard():
    # Load dashboard template
    template_path = os.path.join(os.path.dirname(__file__), "templates", "index.html")
    if os.path.exists(template_path):
        with open(template_path, "r", encoding="utf-8") as f:
            return f.read()
    else:
        # Fallback inline simple layout if template not found
        return """
        <html>
            <head><title>Apex Store Intelligence Dashboard</title></head>
            <body style='background-color:#121214; color:#fff; font-family:sans-serif; text-align:center; padding-top:100px;'>
                <h1>Apex Store Intelligence</h1>
                <p>Dashboard UI template not found at templates/index.html.</p>
            </body>
        </html>
        """
