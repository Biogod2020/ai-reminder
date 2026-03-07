import os
import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from core.adapter import GeminiAdapter

logger = logging.getLogger("MemoryConsolidator")

class MemoryConsolidator:
    """
    Tiered memory compression system:
    Daily -> 3-Day -> Weekly -> Monthly -> Yearly
    """
    
    def __init__(self, db_url: str = "sqlite:///notion_soul.db"):
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)
        self.adapter = GeminiAdapter()
        self.soul_md_path = "user_soul.md"

    async def consolidate_layer(self, source_category: str, target_category: str, days: int, keep_active_count: int = 0):
        """
        Generic logic to compress memories from one tier into the next.
        """
        start_time = datetime.now(timezone.utc) - timedelta(days=days)
        
        with self.Session() as session:
            # 1. Fetch source memories that are active
            stmt = text("""
                SELECT id, value, updated_at FROM user_soul 
                WHERE category = :cat AND updated_at > :start AND is_active = 1
                ORDER BY updated_at ASC
            """)
            rows = session.execute(stmt, {"cat": source_category, "start": start_time}).fetchall()
            
            if not rows:
                logger.info(f"No active {source_category} records found to consolidate into {target_category}.")
                return

            raw_text = "\n".join([f"- [{r[2]}] {r[1]}" for r in rows])
            
            # 2. AI Summarization & Synthesis
            prompt = f"""
            SYSTEM PROTOCOL: MEMORY CONSOLIDATION (Tier: {target_category})
            
            You are refining the 'Digital Soul' of the user. 
            Your task is to synthesize the following raw behavioral data and lower-tier summaries from the past {days} days into a high-signal {target_category}.
            
            INPUT DATA:
            {raw_text}
            
            INSTRUCTIONS:
            1. Identify persistent habits, productivity peaks, and preferred tools.
            2. Detect shifts in behavior or new preferences.
            3. Synthesize into a concise, professional summary (1-2 paragraphs or 5-7 punchy bullet points).
            4. Do NOT just list the events; explain the 'SOUL' (the pattern behind them).
            
            OUTPUT:
            Concise summary text only.
            """
            
            summary = await self.adapter.generate_content(prompt, include_memory=False)
            
            # 3. Store result in DB
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
            
            # 4. Deactivate old source memories
            ids_to_deactivate = [r[0] for r in rows]
            if keep_active_count > 0:
                ids_to_deactivate = ids_to_deactivate[:-keep_active_count]
            
            if ids_to_deactivate:
                # Direct string formatting for IDs to avoid SQLite parameter issues with tuples
                id_list = ",".join([str(i) for i in ids_to_deactivate])
                deactivate_stmt = text(f"UPDATE user_soul SET is_active = 0 WHERE id IN ({id_list})")
                session.execute(deactivate_stmt)
            
            session.commit()
            
            # 5. Append to Markdown for permanent history
            self._append_to_markdown(target_category, summary.strip())
            logger.info(f"Successfully consolidated {source_category} into {target_category}.")

    def _append_to_markdown(self, tier: str, content: str):
        """Append summaries to the history file with clear hierarchy."""
        with open(self.soul_md_path, "a", encoding="utf-8") as f:
            f.write(f"\n\n## [{tier.upper()}] {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
            f.write(content)

    async def run_maintenance(self, force: bool = False):
        """Main entry point for the 6 AM maintenance task."""
        now = datetime.now()
        logger.info(f"Running Memory Maintenance at {now}")
        
        # 1. Daily: Raw Session -> Daily Summary (Past 24h)
        await self.consolidate_layer("session", "daily_summary", 1, keep_active_count=0)
        
        # 2. 3-Day: Daily -> 3-Day Summary
        if now.day % 3 == 0 or force:
            await self.consolidate_layer("daily_summary", "threeday_summary", 3, keep_active_count=1)
            
        # 3. Weekly: 3-Day -> Weekly Summary
        if now.weekday() == 0 or force: # Monday
            await self.consolidate_layer("threeday_summary", "weekly_summary", 7, keep_active_count=1)
            
        # 4. Monthly: Weekly -> Monthly Summary
        if now.day == 1 or force:
            await self.consolidate_layer("weekly_summary", "monthly_summary", 30, keep_active_count=1)
            
        # 5. Yearly: Monthly -> Yearly
        if (now.month == 1 and now.day == 1) or force:
            await self.consolidate_layer("monthly_summary", "yearly_summary", 365, keep_active_count=1)

        logger.info("Maintenance complete.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    consolidator = MemoryConsolidator()
    asyncio.run(consolidator.run_maintenance(force=True))
