from typing import Dict, Any, List
import sqlite3
import os
import time
from datetime import datetime
from app.database import get_db_connection

# In-memory tracking of the last wall-clock ingestion time per store
LAST_INGEST_WALLCLOCK: Dict[str, float] = {}

def track_ingest_activity(store_id: str):
    LAST_INGEST_WALLCLOCK[store_id] = time.time()

def calculate_service_health() -> Dict[str, Any]:
    warnings = []
    status = "UP"
    last_event_timestamps = {}
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get unique stores in the database
        cursor.execute("SELECT DISTINCT store_id FROM events")
        stores = [r['store_id'] for r in cursor.fetchall()]
        
        # If no stores are in the database yet, we can check the default store ST1008 / STORE_BLR_002
        if not stores:
            stores = ["STORE_BLR_002"]
            
        for store in stores:
            # Query last event timestamp from database
            cursor.execute("SELECT MAX(timestamp) as max_t FROM events WHERE store_id = ?", (store,))
            row = cursor.fetchone()
            last_event_timestamps[store] = row['max_t'] if row and row['max_t'] else None
            
            # Check Stale Feed Warning using wall-clock ingestion activity
            # If the store has events but we haven't received any new POST request in the last 10 minutes (600 seconds)
            last_active = LAST_INGEST_WALLCLOCK.get(store)
            if last_active:
                elapsed = time.time() - last_active
                if elapsed > 600:
                    warnings.append(f"STALE_FEED: No real-time ingestion activity for store '{store}' in the last {round(elapsed / 60, 1)} minutes.")
            else:
                # If there are events in DB but we never logged a live ingestion (e.g. app restarted),
                # check if the database's latest event is stale compared to real time (optional)
                # Let's check if the database itself is empty
                if not last_event_timestamps[store]:
                    warnings.append(f"STALE_FEED: No camera feed events found for store '{store}' in the database.")
                    
        conn.close()
    except Exception as e:
        status = "DOWN"
        warnings.append(f"DATABASE_UNAVAILABLE: {str(e)}")
        
    return {
        "status": status,
        "last_event_timestamp_per_store": last_event_timestamps,
        "warnings": warnings
    }
