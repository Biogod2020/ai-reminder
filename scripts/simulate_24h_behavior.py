import sqlite3
import json
import os
from datetime import datetime, timedelta, timezone

# Simulation Constants
SIM_DB_PATH = ".sim_mem_db.sqlite"
COREDATA_OFFSET = 978307200

def setup_sim_db():
    """Initializes the simulation database schema."""
    if os.path.exists(SIM_DB_PATH):
        os.remove(SIM_DB_PATH)
    
    conn = sqlite3.connect(SIM_DB_PATH)
    cursor = conn.cursor()
    
    # Create user_soul table (matches main DB)
    cursor.execute("""
    CREATE TABLE user_soul (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        key VARCHAR(100) NOT NULL,
        value TEXT NOT NULL,
        category VARCHAR(50) NOT NULL,
        updated_at DATETIME NOT NULL,
        is_active BOOLEAN DEFAULT 1,
        UNIQUE (key)
    );
    """)
    
    # Create omni_behavior_log table
    cursor.execute("""
    CREATE TABLE omni_behavior_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        window_id VARCHAR(50) NOT NULL,
        start_time DATETIME NOT NULL,
        end_time DATETIME NOT NULL,
        layers_json TEXT NOT NULL,
        summary_insight TEXT,
        updated_at DATETIME NOT NULL,
        UNIQUE (window_id)
    );
    """)
    
    conn.commit()
    return conn

def generate_24h_data(conn):
    """Generates a realistic 24-hour behavioral log."""
    cursor = conn.cursor()
    
    # Start time: Yesterday at 00:00
    now = datetime.now(timezone.utc)
    base_time = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    
    # 1. 00:00 - 08:00 : Sleep (Away)
    # No logs in omni_behavior_log for away periods usually, but we can simulate isBacklit if needed.
    # For simplicity, we assume no app usage.
    
    # 2. 08:30 - 09:30 : Morning Routine / Catch up
    add_window(cursor, base_time + timedelta(hours=8, minutes=30), [
        {"app": "Chrome", "category": "UTILITY", "intent": "Checking emails and news", "duration": 600, "score": 0.6},
        {"app": "Slack", "category": "UTILITY", "intent": "Responding to team messages", "duration": 300, "score": 0.7},
        {"app": "Spotify", "category": "LEISURE", "intent": "Listening to focus music", "duration": 900, "score": 0.4}
    ], "Starting the day with light communication and music.")

    # 3. 10:00 - 12:30 : Deep Work (Phase 1)
    add_window(cursor, base_time + timedelta(hours=10), [
        {"app": "VS Code", "category": "WORK", "intent": "Implementing the truth merger logic", "duration": 1800, "score": 0.95},
        {"app": "Terminal", "category": "WORK", "intent": "Running unit tests and debugging SQL", "duration": 600, "score": 0.9},
        {"app": "Chrome", "category": "WORK", "intent": "Searching for SQLite upsert syntax", "duration": 300, "score": 0.8},
        {"app": "VS Code", "category": "WORK", "intent": "Refactoring the consolidator engine", "duration": 2400, "score": 0.98}
    ], "High-intensity technical execution. Deep flow state detected.")

    # 4. 12:30 - 13:30 : Lunch Break (Leisure)
    add_window(cursor, base_time + timedelta(hours=12, minutes=30), [
        {"app": "YouTube", "category": "LEISURE", "intent": "Watching technical keynotes while eating", "duration": 1800, "score": 0.3},
        {"app": "Chrome", "category": "LEISURE", "intent": "Browsing tech blogs", "duration": 600, "score": 0.4}
    ], "Cognitive recharge period.")

    # 5. 14:00 - 16:00 : Fragmented Afternoon (Meeting + Admin)
    add_window(cursor, base_time + timedelta(hours=14), [
        {"app": "Zoom", "category": "WORK", "intent": "Weekly sync with the agent team", "duration": 1800, "score": 0.75},
        {"app": "Chrome", "category": "LEISURE", "intent": "Distracted browsing after meeting", "duration": 300, "score": 0.2},
        {"app": "Slack", "category": "UTILITY", "intent": "Updating status and documentation", "duration": 600, "score": 0.6},
        {"app": "Antigravity", "category": "UNCATEGORIZED", "intent": "No visual data (Sampling gap)", "duration": 120, "score": 0.0}
    ], "Fragmented period with context switching and a visual sampling gap.")

    # 6. 20:00 - 22:00 : Late Night Deep Dive
    add_window(cursor, base_time + timedelta(hours=20), [
        {"app": "PyCharm", "category": "WORK", "intent": "Developing the 24h simulation script", "duration": 3600, "score": 0.96},
        {"app": "Arc", "category": "WORK", "intent": "Reading Gemini 3.1 documentation", "duration": 1200, "score": 0.9}
    ], "Secondary focus peak. User prefers quiet hours for complex scripting.")

    conn.commit()

def add_window(cursor, start_dt, events, summary):
    """Adds a 30-min window entry to the simulation DB."""
    end_dt = start_dt + timedelta(minutes=30)
    window_id = f"sim_window_{start_dt.strftime('%Y%m%d_%H%M')}"
    
    merged_timeline = []
    current_time = start_dt
    for e in events:
        merged_timeline.append({
            "start": current_time.isoformat(),
            "duration": e["duration"],
            "app": e["app"],
            "inferred_category": e["category"],
            "visual_context": e["intent"],
            "focus_score": e["score"],
            "is_smoothed": e["score"] == 0.0
        })
        current_time += timedelta(seconds=e["duration"])
        
    cursor.execute("""
    INSERT INTO omni_behavior_log (window_id, start_time, end_time, layers_json, summary_insight, updated_at)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        window_id,
        start_dt.isoformat(),
        end_dt.isoformat(),
        json.dumps(merged_timeline),
        summary,
        datetime.now(timezone.utc).isoformat()
    ))

if __name__ == "__main__":
    conn = setup_sim_db()
    generate_24h_data(conn)
    conn.close()
    print(f"Simulation data generated successfully at {SIM_DB_PATH}")
