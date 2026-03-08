import asyncio
import os
import sys
import logging
from datetime import datetime

# Ensure project root is in path
sys.path.append(os.getcwd())

from core.consolidator import MemoryConsolidator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

SIM_DB_URL = "sqlite:///.sim_mem_db.sqlite"

async def run_stress_test():
    print("\n" + "="*60)
    print("🚀 STARTING DUAL-AXIS CONSOLIDATION STRESS TEST")
    print("="*60)
    
    # Initialize consolidator with SIM DB
    consolidator = MemoryConsolidator(db_url=SIM_DB_URL)
    
    # 1. Trigger Daily Consolidation
    print("\n--- 🟢 STEP 1: Daily Consolidation (Perception -> Daily) ---")
    # We pass force=True to ensure it runs even if it's not 6 AM
    # Note: consolidate_layer targets 'daily_summary' from 'session'
    # Actually, my update to consolidator.py targets 'daily_summary' from 'omni_behavior_log'
    await consolidator.consolidate_layer("session", "daily_summary", days=1)
    
    # 2. Trigger 3-Day Consolidation
    print("\n--- 🟢 STEP 2: 3-Day Consolidation (Daily -> 3-Day) ---")
    await consolidator.consolidate_layer("daily_summary", "threeday_summary", days=3, keep_active_count=1)
    
    # 3. Trigger Weekly Consolidation
    print("\n--- 🟢 STEP 3: Weekly Consolidation (3-Day -> Weekly) ---")
    await consolidator.consolidate_layer("threeday_summary", "weekly_summary", days=7, keep_active_count=1)
    
    print("\n" + "="*60)
    print("📜 FINAL SOUL HIERARCHY REVIEW")
    print("="*60)
    
    # Display the results from the DB
    from sqlalchemy import create_engine, text
    engine = create_engine(SIM_DB_URL)
    with engine.connect() as conn:
        stmt = text("SELECT category, value, updated_at FROM user_soul ORDER BY updated_at ASC")
        rows = conn.execute(stmt).fetchall()
        for cat, val, updated in rows:
            print(f"\n[{cat.upper()}] (Generated: {updated})")
            print("-" * 20)
            print(val)
            print("-" * 20)

if __name__ == "__main__":
    asyncio.run(run_stress_test())
