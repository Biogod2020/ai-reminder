import os
import asyncio
import logging
import sqlite3
import shutil
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from core.adapter import GeminiAdapter

logger = logging.getLogger("MemoryConsolidator")

# CoreData timestamp offset for macOS
COREDATA_OFFSET = 978307200

class MemoryConsolidator:
    """
    Tiered memory compression system:
    Daily -> 3-Day -> Weekly -> Monthly -> Yearly
    Includes macOS Screen Time integration for high-fidelity behavior tracking.
    """
    
    def __init__(self, db_url: str = "sqlite:///notion_soul.db"):
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)
        self.adapter = GeminiAdapter()
        self.soul_md_path = "user_soul.md"
        self.knowledge_db_path = os.path.expanduser("~/Library/Application Support/Knowledge/knowledgeC.db")

    def _get_screen_time_data(self, days_back: int = 1) -> str:
        """Extracts application usage from macOS knowledgeC.db."""
        if not os.path.exists(self.knowledge_db_path):
            return "No macOS Screen Time database found."

        tmp_db = "knowledgeC_maintenance_tmp.db"
        try:
            shutil.copy2(self.knowledge_db_path, tmp_db)
            conn = sqlite3.connect(tmp_db)
            cursor = conn.cursor()

            # Time range calculation
            now = datetime.now()
            start_date = (now - timedelta(days=days_back)).replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=days_back)

            start_ts = int(start_date.timestamp()) - COREDATA_OFFSET
            end_ts = int(end_date.timestamp()) - COREDATA_OFFSET

            query = """
            SELECT ZVALUESTRING, SUM(ZENDDATE - ZSTARTDATE) as total_seconds 
            FROM ZOBJECT 
            WHERE ZSTREAMNAME = '/app/usage' 
            AND ZSTARTDATE >= ? AND ZSTARTDATE < ?
            GROUP BY ZVALUESTRING 
            ORDER BY total_seconds DESC
            """
            cursor.execute(query, (start_ts, end_ts))
            rows = cursor.fetchall()
            
            report = []
            for bundle_id, seconds in rows:
                if seconds < 60: continue
                minutes = seconds // 60
                hours = minutes // 60
                time_str = f"{hours}h {minutes % 60}m" if hours > 0 else f"{minutes}m"
                app_name = bundle_id.split('.')[-1].capitalize()
                report.append(f"- {app_name}: {time_str}")
            
            conn.close()
            os.remove(tmp_db)
            return "\n".join(report) if report else "No significant app usage detected."
        except Exception as e:
            if os.path.exists(tmp_db): os.remove(tmp_db)
            return f"Error extracting Screen Time: {e}"

    async def consolidate_layer(self, source_category: str, target_category: str, days: int, keep_active_count: int = 0):
        """Generic logic to compress memories from one tier into the next."""
        start_time = datetime.now(timezone.utc) - timedelta(days=days)
        
        # Additional Context: For Daily Summary, we inject real Screen Time data
        extra_context = ""
        if target_category == "daily_summary":
            logger.info("Injecting macOS Screen Time data into Daily Summary...")
            screen_time = self._get_screen_time_data(days_back=1)
            extra_context = f"\nMACOS SCREEN TIME (ACTUAL USAGE):\n{screen_time}\n"

        with self.Session() as session:
            # 1. Fetch active source memories
            stmt = text("""
                SELECT id, value, updated_at FROM user_soul 
                WHERE category = :cat AND updated_at > :start AND is_active = 1
                ORDER BY updated_at ASC
            """)
            rows = session.execute(stmt, {"cat": source_category, "start": start_time}).fetchall()
            
            if not rows and not extra_context:
                logger.info(f"No data found to consolidate into {target_category}.")
                return

            raw_text = "\n".join([f"- [{r[2]}] {r[1]}" for r in rows])
            
            # 2. AI Summarization
            prompt = f"""
            SYSTEM PROTOCOL: MEMORY CONSOLIDATION (Tier: {target_category})
            
            You are refining the 'Digital Soul' of the user. 
            Synthesize the following behavioral data into a high-signal {target_category}.
            
            {extra_context}
            
            INTERNAL AGENT LOGS (SAMPLED):
            {raw_text}
            
            INSTRUCTIONS:
            1. Cross-reference the Agent Logs with the Actual Usage (if available).
            2. Identify productivity trends, focus blocks, and potential burnout risks.
            3. Synthesize into a concise, professional summary.
            4. Output should be strictly the summary text.
            """
            
            summary = await self.adapter.generate_content(prompt, include_memory=False)
            
            # 3. Store result
            timestamp = datetime.now().strftime("%Y-%m-%d")
            key = f"{target_category}:{timestamp}"
            
            upsert_stmt = text("""
                INSERT INTO user_soul (key, value, category, updated_at, is_active)
                VALUES (:key, :value, :category, :updated_at, 1)
                ON CONFLICT(key) DO UPDATE SET
                    value = excluded.value,
                    updated_at = excluded.updated_at,
                    is_active = 1
            """)
            session.execute(upsert_stmt, {
                "key": key,
                "value": summary.strip(),
                "category": target_category,
                "updated_at": datetime.now(timezone.utc)
            })
            
            # 4. Deactivate old source records
            ids_to_deactivate = [r[0] for r in rows]
            if keep_active_count > 0:
                ids_to_deactivate = ids_to_deactivate[:-keep_active_count]
            
            if ids_to_deactivate:
                id_list = ",".join([str(i) for i in ids_to_deactivate])
                session.execute(text(f"UPDATE user_soul SET is_active = 0 WHERE id IN ({id_list})"))
            
            session.commit()
            self._append_to_markdown(target_category, summary.strip())
            logger.info(f"Successfully consolidated into {target_category}.")

    def _append_to_markdown(self, tier: str, content: str):
        with open(self.soul_md_path, "a", encoding="utf-8") as f:
            f.write(f"\n\n## [{tier.upper()}] {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
            f.write(content)

    async def run_maintenance(self, force: bool = False):
        now = datetime.now()
        logger.info(f"Running Maintenance at {now}")
        
        await self.consolidate_layer("session", "daily_summary", 1, keep_active_count=0)
        
        if now.day % 3 == 0 or force:
            await self.consolidate_layer("daily_summary", "threeday_summary", 3, keep_active_count=1)
        if now.weekday() == 0 or force:
            await self.consolidate_layer("threeday_summary", "weekly_summary", 7, keep_active_count=1)
        if now.day == 1 or force:
            await self.consolidate_layer("weekly_summary", "monthly_summary", 30, keep_active_count=1)
        if (now.month == 1 and now.day == 1) or force:
            await self.consolidate_layer("monthly_summary", "yearly_summary", 365, keep_active_count=1)

        logger.info("Maintenance complete.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    consolidator = MemoryConsolidator()
    asyncio.run(consolidator.run_maintenance(force=True))
