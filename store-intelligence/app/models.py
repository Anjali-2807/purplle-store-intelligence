from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class EventMetadata(BaseModel):
    queue_depth: Optional[int] = None
    sku_zone: Optional[str] = None
    session_seq: Optional[int] = None

class EventModel(BaseModel):
    event_id: str
    store_id: str
    camera_id: str
    visitor_id: str
    event_type: str
    timestamp: str
    zone_id: Optional[str] = None
    dwell_ms: Optional[int] = 0
    is_staff: Optional[bool] = False
    confidence: Optional[float] = 1.0
    metadata: Optional[EventMetadata] = None

class IngestResponse(BaseModel):
    status: str
    processed_count: int
    failed_count: int
    errors: List[Dict[str, Any]] = []

class StoreMetricsResponse(BaseModel):
    store_id: str
    unique_visitors: int
    conversion_rate: float
    avg_dwell_per_zone: Dict[str, float]
    queue_depth: int
    abandonment_rate: float

class FunnelStage(BaseModel):
    stage_name: str
    visitor_count: int
    conversion_pct: float
    drop_off_pct: float

class StoreFunnelResponse(BaseModel):
    store_id: str
    funnel: List[FunnelStage]

class HeatmapGridCell(BaseModel):
    zone_id: str
    visit_frequency: int
    avg_dwell_ms: float
    normalized_score: float # 0 to 100

class StoreHeatmapResponse(BaseModel):
    store_id: str
    heatmap: List[HeatmapGridCell]
    data_confidence: bool

class AnomalyModel(BaseModel):
    anomaly_type: str # QUEUE_SPIKE, CONVERSION_DROP, DEAD_ZONE
    severity: str # INFO, WARN, CRITICAL
    timestamp: str
    details: str
    suggested_action: str

class StoreAnomaliesResponse(BaseModel):
    store_id: str
    anomalies: List[AnomalyModel]

class HealthStatusResponse(BaseModel):
    status: str
    last_event_timestamp_per_store: Dict[str, Optional[str]]
    warnings: List[str]
