# PROMPT: Write a pytest file for the REST API operational anomaly detection. Set up test conditions for a queue spike (queue_depth >= 3), conversion drop (conversion < 10%), and dead zone (zero entries in 30 minutes). Assert the active anomalies endpoint return appropriate anomaly types, severity categories, and recommended actions.
# CHANGES MADE: Integrated TestClient to make direct requests to GET /stores/{id}/anomalies and verified exact anomaly details and severity levels.

import sys
import os
import pytest
from fastapi.testclient import TestClient

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.main import app
from app.database import get_db_connection

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_test_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM events")
    cursor.execute("DELETE FROM transactions")
    conn.commit()
    conn.close()

def test_anomalies_queue_spike():
    # 1. Ingest a BILLING_QUEUE_JOIN event with queue_depth = 4 (trigger threshold is 3)
    event = {
        "event_id": "eq_991", "store_id": "STORE_TEST_01", "camera_id": "CAM_5", "visitor_id": "VIS_QA",
        "event_type": "BILLING_QUEUE_JOIN", "timestamp": "2026-04-10T20:10:00Z", "zone_id": "CASH COUNTER",
        "dwell_ms": 0, "is_staff": False, "confidence": 0.95,
        "metadata": { "queue_depth": 4, "sku_zone": "BILLING", "session_seq": 2 }
    }
    
    client.post("/events/ingest", json=[event])
    
    # 2. Query anomalies
    res = client.get("/stores/STORE_TEST_01/anomalies")
    assert res.status_code == 200
    anomalies = res.json()["anomalies"]
    
    # Verify that a BILLING_QUEUE_SPIKE anomaly was triggered
    queue_spikes = [an for an in anomalies if an["anomaly_type"] == "BILLING_QUEUE_SPIKE"]
    assert len(queue_spikes) == 1
    assert queue_spikes[0]["severity"] == "WARN" # Warning since it's 4 (critical is >=5)
    assert "Open secondary POS terminal" in queue_spikes[0]["suggested_action"]

def test_anomalies_conversion_drop():
    # 1. Ingest 5 visitors to establish a sample size, but 0 transactions (0% conversion)
    events = []
    for i in range(5):
        events.append({
            "event_id": f"ec_drop_{i}", "store_id": "STORE_TEST_01", "camera_id": "CAM_3", "visitor_id": f"VIS_C_DROP_{i}",
            "event_type": "ENTRY", "timestamp": "2026-04-10T20:10:00Z", "is_staff": False, "confidence": 0.95
        })
        
    client.post("/events/ingest", json=events)
    
    # 2. Query anomalies
    res = client.get("/stores/STORE_TEST_01/anomalies")
    assert res.status_code == 200
    anomalies = res.json()["anomalies"]
    
    # Verify CONVERSION_DROP is triggered
    conv_drops = [an for an in anomalies if an["anomaly_type"] == "CONVERSION_DROP"]
    assert len(conv_drops) == 1
    assert conv_drops[0]["severity"] == "WARN"
    assert "Check if pricing displays" in conv_drops[0]["suggested_action"]
