import json
import uuid
import os
from urllib import request as urllib_request
from datetime import datetime

class EventEmitter:
    def __init__(self, output_jsonl_path="events_output.jsonl", api_url="http://localhost:8000/events/ingest"):
        self.output_jsonl_path = output_jsonl_path
        self.api_url = api_url
        self.batch_queue = []
        
        # Clear output file on start
        if os.path.exists(output_jsonl_path):
            try:
                os.remove(output_jsonl_path)
            except Exception:
                pass

    def validate_event(self, event: dict) -> bool:
        required_keys = [
            "event_id", "store_id", "camera_id", "visitor_id", 
            "event_type", "timestamp", "zone_id", "dwell_ms", 
            "is_staff", "confidence"
        ]
        # Check all required keys exist (even if None)
        for key in required_keys:
            if key not in event:
                print(f"Validation Error: missing key '{key}'")
                return False
                
        # Schema compliance checks
        if not isinstance(event["event_id"], str): return False
        if not isinstance(event["store_id"], str): return False
        if not isinstance(event["camera_id"], str): return False
        if not isinstance(event["visitor_id"], str): return False
        if not isinstance(event["event_type"], str): return False
        if not isinstance(event["timestamp"], str): return False
        if event["dwell_ms"] is not None and not isinstance(event["dwell_ms"], (int, float)): return False
        if not isinstance(event["is_staff"], bool): return False
        if not isinstance(event["confidence"], (int, float)): return False
        
        return True

    def emit(self, event: dict, send_to_api=True):
        # 1. Fill default values if missing
        if "event_id" not in event or not event["event_id"]:
            event["event_id"] = str(uuid.uuid4())
        if "metadata" not in event or event["metadata"] is None:
            event["metadata"] = {
                "queue_depth": None,
                "sku_zone": None,
                "session_seq": 1
            }
            
        # 2. Validate
        if not self.validate_event(event):
            print(f"Skipping malformed event: {event}")
            return
            
        # 3. Write locally to JSONL file
        try:
            with open(self.output_jsonl_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(event) + "\n")
        except Exception as e:
            print(f"Error writing event to JSONL file: {e}")
            
        # 4. Add to batch queue
        if send_to_api:
            self.batch_queue.append(event)
            if len(self.batch_queue) >= 50: # Flush every 50 events
                self.flush()

    def flush(self):
        if not self.batch_queue:
            return
            
        payload = self.batch_queue
        self.batch_queue = []
        
        print(f"Posting batch of {len(payload)} events to API {self.api_url}...")
        
        try:
            # We use standard library urllib to avoid requests package dependency in minimal setups
            data = json.dumps(payload).encode('utf-8')
            req = urllib_request.Request(
                self.api_url, 
                data=data, 
                headers={'Content-Type': 'application/json'}
            )
            with urllib_request.urlopen(req, timeout=5) as response:
                res_body = response.read().decode('utf-8')
                res_json = json.loads(res_body)
                print(f"API Ingest Success: {res_json['processed_count']} processed, {res_json['failed_count']} failed.")
        except Exception as e:
            print(f"Failed to post events batch to API: {e}")
