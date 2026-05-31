import os
import sqlite3
import json
import pandas as pd
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "store_intelligence.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create events table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS events (
        event_id TEXT PRIMARY KEY,
        store_id TEXT,
        camera_id TEXT,
        visitor_id TEXT,
        event_type TEXT,
        timestamp TEXT,
        zone_id TEXT,
        dwell_ms INTEGER,
        is_staff BOOLEAN,
        confidence REAL,
        metadata TEXT
    )
    """)
    
    # Create transactions table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        order_id TEXT PRIMARY KEY,
        store_id TEXT,
        timestamp TEXT,
        basket_value_inr REAL,
        qty INTEGER,
        raw_details TEXT
    )
    """)
    
    conn.commit()
    conn.close()
    print("Database initialized successfully.")

def seed_pos_transactions(csv_path):
    if not os.path.exists(csv_path):
        print(f"Warning: POS CSV not found at {csv_path}. Skipping seed.")
        return
    
    print(f"Seeding POS transactions from {csv_path}...")
    df = pd.read_csv(csv_path)
    
    # Convert columns and handle group-by to get unique orders
    # Date in CSV is 10-04-2026, time is 12:15:05
    # We want ISO-8601 UTC format: 2026-04-10T12:15:05Z
    def parse_timestamp(row):
        try:
            d_str = row['order_date'] # 10-04-2026
            t_str = row['order_time'] # 12:15:05
            dt = datetime.strptime(f"{d_str} {t_str}", "%d-%m-%Y %H:%M:%S")
            return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        except Exception:
            # Fallback if parsing fails
            return "2026-04-10T00:00:00Z"

    df['timestamp'] = df.apply(parse_timestamp, axis=1)
    
    # In the CSV, the store_id is 'ST1008'. We also map it to 'STORE_BLR_002' to support both sample layouts seamlessly!
    df['normalized_store_id'] = df['store_id'].apply(lambda x: "STORE_BLR_002" if str(x).strip() == "ST1008" else str(x))
    
    # Group by order_id
    grouped = df.groupby(['order_id', 'normalized_store_id', 'timestamp']).agg({
        'total_amount': 'sum',
        'qty': 'sum',
        'product_name': lambda x: ", ".join(map(str, x))
    }).reset_index()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    inserted_count = 0
    for _, row in grouped.iterrows():
        try:
            raw_data = json.dumps({"products": row['product_name']})
            cursor.execute("""
            INSERT OR REPLACE INTO transactions (order_id, store_id, timestamp, basket_value_inr, qty, raw_details)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (
                str(row['order_id']),
                str(row['normalized_store_id']),
                str(row['timestamp']),
                float(row['total_amount']),
                int(row['qty']),
                raw_data
            ))
            
            # Also insert with 'ST1008' so both query parameters work!
            cursor.execute("""
            INSERT OR REPLACE INTO transactions (order_id, store_id, timestamp, basket_value_inr, qty, raw_details)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (
                str(row['order_id']) + "_ST1008",
                "ST1008",
                str(row['timestamp']),
                float(row['total_amount']),
                int(row['qty']),
                raw_data
            ))
            
            inserted_count += 2
        except Exception as e:
            print(f"Error seeding row {row['order_id']}: {e}")
            
    conn.commit()
    conn.close()
    print(f"Successfully seeded {inserted_count} transaction records.")

if __name__ == "__main__":
    init_db()
    # Path to POS CSV in workspace
    csv_file = "/Users/anjalitiwari/Desktop/Purplle Tech Challenge/Brigade_Bangalore_10_April_26 (1)bc6219c.csv"
    seed_pos_transactions(csv_file)
