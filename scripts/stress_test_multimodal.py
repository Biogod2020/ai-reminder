import asyncio
import os
import sys
import logging
import time
import shutil
from datetime import datetime, timedelta, timezone

# Ensure project root is in path
sys.path.append(os.getcwd())

from core.visual_sampler import VisualSampler
from core.system_db import KnowledgeDB
from core.synthesis_engine import BehaviorSynthesisEngine
from core.memory import SharedMemoryManager

# Configure logging to be very verbose for the stress test
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger("MultimodalStressTest")

async def run_stress_test():
    logger.info("🚀 STARTING MULTIMODAL TRUTH ENGINE STRESS TEST")
    logger.info("--------------------------------------------------")
    logger.info("EXPECTED PERMISSION PROMPTS:")
    logger.info("1. Screen Recording (for screenshots)")
    logger.info("2. Accessibility (for window titles)")
    logger.info("3. Full Disk Access (for knowledgeC.db)")
    logger.info("--------------------------------------------------")

    sampler = VisualSampler(capture_dir="stress_captures")
    db = KnowledgeDB()
    engine = BehaviorSynthesisEngine()
    # Point engine to the stress captures
    engine.capture_dir = "stress_captures"
    
    try:
        # STEP 1: Verify Permissions & High-Frequency Sampling
        logger.info("STEP 1: Starting High-Frequency Sampling (5 images, 5s interval)...")
        captured_files = []
        for i in range(5):
            logger.info(f"   Capture Attempt {i+1}/5...")
            # This will trigger the 'Screen Recording' prompt if not granted
            path = sampler.capture_and_process()
            if path:
                logger.info(f"   ✅ Captured: {path}")
                captured_files.append(path)
            else:
                logger.error("   ❌ Capture FAILED. Please check Screen Recording permissions.")
            await asyncio.sleep(5)

        if not captured_files:
            logger.error("No images captured. Aborting test.")
            return

        # STEP 2: Verify System DB Access
        logger.info("STEP 2: Verifying knowledgeC.db Access...")
        # This will trigger the 'Full Disk Access' prompt if not granted
        now = datetime.now(timezone.utc)
        timeline = db.get_timeline(now - timedelta(minutes=60), now)
        if timeline:
            logger.info(f"   ✅ Successfully retrieved {len(timeline)} events from system database.")
        else:
            logger.warning("   ⚠️ No timeline events found. This might be a permission issue or low activity.")

        # STEP 3: Live Multimodal Synthesis
        logger.info("STEP 3: Running Live Multimodal Synthesis via Gemini 3.1...")
        # We simulate a 5-minute window to include our freshly captured images
        logger.info("   Sending images and timeline to API...")
        start_time = time.time()
        result = await engine.synthesize_window(minutes=10, delete_after=False)
        duration = time.time() - start_time

        if result:
            logger.info(f"   ✅ Synthesis COMPLETE in {duration:.2f}s")
            logger.info(f"   📊 AI Summary: {result.get('summary')[:100]}...")
            logger.info(f"   🏷️ Categories: {[t.get('category') for t in result.get('timeline', [])]}")
        else:
            logger.error("   ❌ Synthesis FAILED. Check API logs or network.")

        # STEP 4: Memory Persistence Check
        logger.info("STEP 4: Verifying Memory Persistence...")
        memory = SharedMemoryManager()
        slices = await memory.search("", scope="truth_slice")
        if any(s for s in slices if s['scope'] == 'truth_slice'):
            logger.info("   ✅ Truth Slice successfully persisted to SQLite.")
        else:
            logger.error("   ❌ Truth Slice not found in database.")

    except Exception as e:
        logger.error(f"💥 CRITICAL TEST FAILURE: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        logger.info("CLEANUP: Removing stress test artifacts...")
        if os.path.exists("stress_captures"):
            shutil.rmtree("stress_captures")
        logger.info("STRESS TEST FINISHED.")

if __name__ == "__main__":
    asyncio.run(run_stress_test())
