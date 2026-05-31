from typing import Dict, Any, List
import sqlite3
from app.database import get_db_connection
from app.metrics import calculate_store_metrics # We can reuse the conversion check logic!

def calculate_store_funnel(store_id: str) -> Dict[str, Any]:
    # We will get the conversion metric to know the purchase count and converted visitors
    metrics = calculate_store_metrics(store_id)
    unique_visitors = metrics["unique_visitors"]
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Entry Count
    # Unique customer visitor_ids who have an ENTRY or any event
    cursor.execute("""
    SELECT DISTINCT visitor_id 
    FROM events 
    WHERE store_id = ? AND is_staff = 0
    """, (store_id,))
    entry_visitors = {r['visitor_id'] for r in cursor.fetchall()}
    entry_count = len(entry_visitors)
    
    # 2. Zone Visit Count
    # Unique customer visitor_ids who entered any zone (excluding entry/exit, backroom, or billing)
    cursor.execute("""
    SELECT DISTINCT visitor_id 
    FROM events 
    WHERE store_id = ? AND is_staff = 0 
      AND zone_id IS NOT NULL 
      AND LOWER(zone_id) NOT IN ('entry', 'exit', 'backroom', 'storage', 'billing', 'cash', 'checkout')
    """, (store_id,))
    zone_visitors = {r['visitor_id'] for r in cursor.fetchall()}
    # Zone visit count must be <= entry count (a visitor must enter to visit a zone)
    # Let's ensure it's a subset
    zone_visitors = zone_visitors.intersection(entry_visitors)
    zone_count = len(zone_visitors)
    
    # 3. Billing Queue Count
    # Unique customer visitor_ids who joined queue or entered billing zone
    cursor.execute("""
    SELECT DISTINCT visitor_id 
    FROM events 
    WHERE store_id = ? AND is_staff = 0 
      AND (
        event_type = 'BILLING_QUEUE_JOIN' OR
        camera_id = 'CAM_5' OR
        LOWER(zone_id) IN ('billing', 'cash', 'checkout', 'cash counter', 'cash_counter')
      )
    """, (store_id,))
    queue_visitors = {r['visitor_id'] for r in cursor.fetchall()}
    queue_visitors = queue_visitors.intersection(entry_visitors)
    queue_count = len(queue_visitors)
    
    # 4. Purchase Count
    # We can fetch the list of converted visitor_ids using the same 5-minute correlation rule!
    # Let's re-run that query or logic here:
    cursor.execute("""
    SELECT visitor_id, timestamp 
    FROM events 
    WHERE store_id = ? AND is_staff = 0 
      AND (
        LOWER(zone_id) LIKE '%billing%' OR 
        LOWER(zone_id) LIKE '%cash%' OR 
        LOWER(zone_id) LIKE '%checkout%' OR 
        camera_id = 'CAM_5' OR
        event_type = 'BILLING_QUEUE_JOIN'
      )
    """, (store_id,))
    billing_events = cursor.fetchall()
    
    cursor.execute("SELECT timestamp FROM transactions WHERE store_id = ?", (store_id,))
    transactions = cursor.fetchall()
    
    from datetime import datetime
    txn_times = []
    for txn in transactions:
        try:
            t_str = txn['timestamp'].replace('Z', '')
            txn_times.append(datetime.fromisoformat(t_str))
        except Exception:
            continue
            
    purchase_visitors = set()
    for b_event in billing_events:
        visitor_id = b_event['visitor_id']
        try:
            b_str = b_event['timestamp'].replace('Z', '')
            t_billing = datetime.fromisoformat(b_str)
            for t_txn in txn_times:
                time_diff = (t_txn - t_billing).total_seconds()
                if 0 <= time_diff <= 300: # 5 minutes
                    purchase_visitors.add(visitor_id)
                    break
        except Exception:
            continue
            
    purchase_visitors = purchase_visitors.intersection(entry_visitors)
    purchase_count = len(purchase_visitors)
    
    conn.close()
    
    # Let's construct the funnel stages
    # Stage 1: Entry
    s1_conv = 1.0 if entry_count > 0 else 0.0
    s1_drop = 0.0
    
    # Stage 2: Zone Visit
    s2_conv = zone_count / entry_count if entry_count > 0 else 0.0
    s2_drop = 1.0 - (zone_count / entry_count) if entry_count > 0 else 0.0
    
    # Stage 3: Billing Queue
    s3_conv = queue_count / entry_count if entry_count > 0 else 0.0
    s3_drop = 1.0 - (queue_count / zone_count) if zone_count > 0 else 0.0
    
    # Stage 4: Purchase
    s4_conv = purchase_count / entry_count if entry_count > 0 else 0.0
    s4_drop = 1.0 - (purchase_count / queue_count) if queue_count > 0 else 0.0
    
    funnel = [
        {
            "stage_name": "Entry",
            "visitor_count": entry_count,
            "conversion_pct": round(s1_conv * 100, 2),
            "drop_off_pct": round(s1_drop * 100, 2)
        },
        {
            "stage_name": "Zone Visit",
            "visitor_count": zone_count,
            "conversion_pct": round(s2_conv * 100, 2),
            "drop_off_pct": round(s2_drop * 100, 2)
        },
        {
            "stage_name": "Billing Queue",
            "visitor_count": queue_count,
            "conversion_pct": round(s3_conv * 100, 2),
            "drop_off_pct": round(s3_drop * 100, 2)
        },
        {
            "stage_name": "Purchase",
            "visitor_count": purchase_count,
            "conversion_pct": round(s4_conv * 100, 2),
            "drop_off_pct": round(s4_drop * 100, 2)
        }
    ]
    
    return {
        "store_id": store_id,
        "funnel": funnel
    }
