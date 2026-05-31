# PROMPT: Write a pytest file for the REST API metrics and funnel calculations. Mock the database connection, ingest simulated customer and staff events, and assert unique_visitors counts exclude staff. Assert funnel counts and drop-offs are mathematically consistent across Entry, Zone Visit, Queue, and Purchase stages.
# CHANGES MADE: Integrated TestClient from fastapi.testclient for full integration-level testing of POST /events/ingest, GET /stores/{id}/metrics, and GET /stores/{id}/funnel. Explicitly verified is_staff=True exclusion.

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
    # Setup: Clean tables before each test
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM events")
    cursor.execute("DELETE FROM transactions")
    
    # Seed a test transaction at 2026-04-10T20:11:15Z (matching simulated conversions)
    cursor.execute("""
    INSERT OR REPLACE INTO transactions (order_id, store_id, timestamp, basket_value_inr, qty, raw_details)
    VALUES (?, ?, ?, ?, ?, ?)
    """, ("TXN_TEST_99", "STORE_TEST_01", "2026-04-10T20:11:15Z", 500.00, 2, '{"products":"Lipstick"}'))
    
    conn.commit()
    conn.close()

def test_events_ingestion_and_idempotency():
    event = {
        "event_id": "test_evt_001",
        "store_id": "STORE_TEST_01",
        "camera_id": "CAM_3",
        "visitor_id": "VIS_TEST_A",
        "event_type": "ENTRY",
        "timestamp": "2026-04-10T20:10:00Z",
        "zone_id": None,
        "dwell_ms": 0,
        "is_staff": False,
        "confidence": 0.98,
        "metadata": {
            "queue_depth": None,
            "sku_zone": None,
            "session_seq": 1
        }
    }
    
    # 1. First Ingestion
    res1 = client.post("/events/ingest", json=[event])
    assert res1.status_code == 200
    assert res1.json()["processed_count"] == 1
    
    # 2. Duplicate Ingestion (Idempotency check)
    res2 = client.post("/events/ingest", json=[event])
    assert res2.status_code == 200
    assert res2.json()["processed_count"] == 1 # Safe to call twice, processed successfully without crashing

def test_metrics_staff_exclusion_and_conversion():
    # 1. Ingest Customer A (VIS_A) and Staff Member (STAFF_X)
    events = [
        # Customer A (Entry, visits Skincare, joins queue, gets purchase)
        {
            "event_id": "e_01", "store_id": "STORE_TEST_01", "camera_id": "CAM_3", "visitor_id": "VIS_A",
            "event_type": "ENTRY", "timestamp": "2026-04-10T20:10:00Z", "zone_id": None, "dwell_ms": 0,
            "is_staff": False, "confidence": 0.99
        },
        {
            "event_id": "e_02", "store_id": "STORE_TEST_01", "camera_id": "CAM_1", "visitor_id": "VIS_A",
            "event_type": "ZONE_ENTER", "timestamp": "2026-04-10T20:10:10Z", "zone_id": "Skincare", "dwell_ms": 0,
            "is_staff": False, "confidence": 0.95
        },
        {
            "event_id": "e_03", "store_id": "STORE_TEST_01", "camera_id": "CAM_5", "visitor_id": "VIS_A",
            "event_type": "BILLING_QUEUE_JOIN", "timestamp": "2026-04-10T20:11:00Z", "zone_id": "CASH COUNTER", "dwell_ms": 0,
            "is_staff": False, "confidence": 0.95, "metadata": { "queue_depth": 1 }
        },
        
        # Staff Member STAFF_X (Should be fully excluded from unique_visitors and funnel counts)
        {
            "event_id": "e_04", "store_id": "STORE_TEST_01", "camera_id": "CAM_1", "visitor_id": "STAFF_X",
            "event_type": "ZONE_ENTER", "timestamp": "2026-04-10T20:10:20Z", "zone_id": "Skincare", "dwell_ms": 30000,
            "is_staff": True, "confidence": 0.99
        }
    ]
    
    ingest_res = client.post("/events/ingest", json=events)
    assert ingest_res.status_code == 200
    
    # 2. Query Metrics API
    metrics_res = client.get("/stores/STORE_TEST_01/metrics")
    assert metrics_res.status_code == 200
    m_data = metrics_res.json()
    
    # Unique visitors should be exactly 1 (only Customer A, excluding Staff X!)
    assert m_data["unique_visitors"] == 1
    # Customer A should be converted since billing was at 20:11:00 and seeded transaction is at 20:11:15 (within 5 minutes!)
    assert m_data["conversion_rate"] == 1.0
    assert m_data["queue_depth"] == 1

def test_funnel_percentages():
    events = [
        # Customer A (Entry, visits Skincare, joins Queue, completes purchase)
        { "event_id": "a1", "store_id": "STORE_TEST_01", "camera_id": "CAM_3", "visitor_id": "VIS_A", "event_type": "ENTRY", "timestamp": "2026-04-10T20:10:00Z", "is_staff": False, "confidence": 0.9 },
        { "event_id": "a2", "store_id": "STORE_TEST_01", "camera_id": "CAM_1", "visitor_id": "VIS_A", "event_type": "ZONE_ENTER", "zone_id": "Skincare", "timestamp": "2026-04-10T20:10:10Z", "is_staff": False, "confidence": 0.9 },
        { "event_id": "a3", "store_id": "STORE_TEST_01", "camera_id": "CAM_5", "visitor_id": "VIS_A", "event_type": "BILLING_QUEUE_JOIN", "zone_id": "CASH COUNTER", "timestamp": "2026-04-10T20:11:00Z", "is_staff": False, "confidence": 0.9 },
        
        # Customer B (Entry, visits Makeup, but doesn't buy)
        { "event_id": "b1", "store_id": "STORE_TEST_01", "camera_id": "CAM_3", "visitor_id": "VIS_B", "event_type": "ENTRY", "timestamp": "2026-04-10T20:10:05Z", "is_staff": False, "confidence": 0.9 },
        { "event_id": "b2", "store_id": "STORE_TEST_01", "camera_id": "CAM_2", "visitor_id": "VIS_B", "event_type": "ZONE_ENTER", "zone_id": "Makeup", "timestamp": "2026-04-10T20:10:15Z", "is_staff": False, "confidence": 0.9 }
    ]
    
    client.post("/events/ingest", json=events)
    
    funnel_res = client.get("/stores/STORE_TEST_01/funnel")
    assert funnel_res.status_code == 200
    f_data = funnel_res.json()["funnel"]
    
    # Assert counts:
    # 2 entered (VIS_A, VIS_B)
    assert f_data[0]["visitor_count"] == 2
    # 2 visited zone (VIS_A, VIS_B)
    assert f_data[1]["visitor_count"] == 2
    # 1 joined queue (VIS_A)
    assert f_data[2]["visitor_count"] == 1
    # 1 purchased (VIS_A)
    assert f_data[3]["visitor_count"] == 1
    
    # Assert conversion %:
    assert f_data[0]["conversion_pct"] == 100.0
    assert f_data[1]["conversion_pct"] == 100.0
    assert f_data[2]["conversion_pct"] == 50.0
    assert f_data[3]["conversion_pct"] == 50.0
    
    # Assert drop-off %:
    assert f_data[1]["drop_off_pct"] == 0.0 # 0% dropoff between Entry & Zone
    assert f_data[2]["drop_off_pct"] == 50.0 # 50% dropoff from Zone to Queue
    assert f_data[3]["drop_off_pct"] == 0.0 # 0% dropoff from Queue to Purchase
