import sqlite3
import os
import shutil
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any

logger = logging.getLogger("SystemDB")

# CoreData timestamp offset for macOS (2001-01-01)
COREDATA_OFFSET = 978307200

class KnowledgeDB:
    """Interface for extracting behavior data from macOS knowledgeC.db."""
    
    def __init__(self):
        self.db_path = os.path.expanduser(
            "~/Library/Application Support/Knowledge/knowledgeC.db"
        )

    def get_timeline(
        self, 
        start_dt: datetime, 
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Extracts application usage events within a specific time window."""
        if not os.path.exists(self.db_path):
            logger.error("knowledgeC.db not found.")
            return []

        tmp_db = "knowledgeC_query_tmp.db"
        try:
            shutil.copy2(self.db_path, tmp_db)
            conn = sqlite3.connect(tmp_db)
            cursor = conn.cursor()

            # Ensure start_ts/end_ts are calculated from UTC timestamps 
            # to match knowledgeC storage
            start_ts = int(start_dt.timestamp()) - COREDATA_OFFSET
            end_ts = int(end_date.timestamp()) - COREDATA_OFFSET

            query = """
            SELECT 
                ZVALUESTRING as bundle_id, 
                ZSTARTDATE, 
                ZENDDATE,
                (ZENDDATE - ZSTARTDATE) as duration
            FROM ZOBJECT 
            WHERE ZSTREAMNAME = '/app/usage' 
            AND ZSTARTDATE >= ? AND ZSTARTDATE < ?
            ORDER BY ZSTARTDATE ASC
            """
            cursor.execute(query, (start_ts, end_ts))
            rows = cursor.fetchall()
            
            events = []
            for bundle_id, start, end, duration in rows:
                if duration < 1: 
                    continue
                
                # Convert back to LOCAL timezone for synthesis alignment
                # (VisualSampler uses local time for filenames)
                event_start = datetime.fromtimestamp(
                    start + COREDATA_OFFSET, 
                    tz=timezone.utc
                ).astimezone() # Convert to local
                
                events.append({
                    "app": bundle_id.split('.')[-1].capitalize(),
                    "bundle_id": bundle_id,
                    "start": event_start.isoformat(),
                    "duration_seconds": int(duration)
                })
            
            conn.close()
            os.remove(tmp_db)
            return events
        except Exception as e:
            logger.error(f"Error querying knowledgeC.db: {e}")
            if os.path.exists(tmp_db): 
                os.remove(tmp_db)
            return []

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    db = KnowledgeDB()
    # Test: last 30 minutes
    now = datetime.now()
    start = now - timedelta(minutes=30)
    timeline = db.get_timeline(start, now)
    for e in timeline:
        print(f"[{e['start']}] {e['app']} - {e['duration_seconds']}s")
