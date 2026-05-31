from typing import Dict, Any, List
import sqlite3
from app.database import get_db_connection

def calculate_store_heatmap(store_id: str) -> Dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check total customer sessions to set data_confidence flag
    cursor.execute("""
    SELECT COUNT(DISTINCT visitor_id) as total_sessions 
    FROM events 
    WHERE store_id = ? AND is_staff = 0
    """, (store_id,))
    s_row = cursor.fetchone()
    total_sessions = s_row['total_sessions'] if s_row and s_row['total_sessions'] else 0
    data_confidence = (total_sessions >= 20)
    
    # Calculate frequency and avg dwell for each physical zone (excluding entry/exit, storage, etc.)
    cursor.execute("""
    SELECT zone_id, COUNT(DISTINCT visitor_id) as visit_frequency, AVG(dwell_ms) as avg_dwell 
    FROM events 
    WHERE store_id = ? AND is_staff = 0 AND zone_id IS NOT NULL 
      AND LOWER(zone_id) NOT IN ('entry', 'exit', 'backroom', 'storage')
    GROUP BY zone_id
    """, (store_id,))
    rows = cursor.fetchall()
    
    heatmap_cells = []
    max_frequency = 0
    
    for row in rows:
        freq = row['visit_frequency'] or 0
        if freq > max_frequency:
            max_frequency = freq
            
    for row in rows:
        zone = row['zone_id']
        freq = row['visit_frequency'] or 0
        dwell = row['avg_dwell'] or 0.0
        
        # Normalize score between 0 and 100 based on visit frequency
        normalized_score = 0.0
        if max_frequency > 0:
            normalized_score = (freq / max_frequency) * 100.0
            
        heatmap_cells.append({
            "zone_id": zone,
            "visit_frequency": freq,
            "avg_dwell_ms": round(dwell, 2),
            "normalized_score": round(normalized_score, 2)
        })
        
    conn.close()
    
    return {
        "store_id": store_id,
        "heatmap": heatmap_cells,
        "data_confidence": data_confidence
    }
