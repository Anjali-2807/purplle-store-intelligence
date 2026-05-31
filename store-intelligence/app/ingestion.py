import json
from typing import List, Dict, Any
from app.models import EventModel
from app.database import get_db_connection

def ingest_events(events_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    processed_count = 0
    failed_count = 0
    errors = []
    
    if len(events_data) > 500:
        return {
            "status": "error",
            "processed_count": 0,
            "failed_count": len(events_data),
            "errors": [{"message": "Batch size exceeds the limit of 500 events."}]
        }
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    for idx, raw_event in enumerate(events_data):
        try:
            # 1. Pydantic validation
            event = EventModel(**raw_event)
            
            # Convert metadata dict to JSON string
            metadata_str = json.dumps(event.metadata.dict()) if event.metadata else "{}"
            
            # 2. Ingest and handle idempotency
            # We use INSERT OR IGNORE to handle duplicate event_ids gracefully
            cursor.execute("""
            INSERT OR IGNORE INTO events (
                event_id, store_id, camera_id, visitor_id, event_type, 
                timestamp, zone_id, dwell_ms, is_staff, confidence, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event.event_id,
                event.store_id,
                event.camera_id,
                event.visitor_id,
                event.event_type,
                event.timestamp,
                event.zone_id,
                event.dwell_ms,
                int(event.is_staff) if event.is_staff is not None else 0,
                event.confidence,
                metadata_str
            ))
            
            # Check if row was actually inserted
            # We can check changes() to see if it was inserted or ignored
            if conn.total_changes > 0:
                processed_count += 1
            else:
                # If row was ignored, it means event_id was already present.
                # Idempotency requirement: it's safe to call twice, so it's a success but not inserted anew.
                processed_count += 1
                
        except Exception as e:
            failed_count += 1
            errors.append({
                "index": idx,
                "event_id": raw_event.get("event_id", "unknown"),
                "message": str(e)
            })
            
    conn.commit()
    conn.close()
    
    return {
        "status": "success" if failed_count == 0 else "partial_success",
        "processed_count": processed_count,
        "failed_count": failed_count,
        "errors": errors
    }
