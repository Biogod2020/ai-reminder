import asyncio
import os
import sys
import logging
import time
from datetime import datetime, timedelta, timezone

# Ensure project root is in path
sys.path.append(os.getcwd())

from core.visual_sampler import VisualSampler
from core.synthesis_engine import BehaviorSynthesisEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger("PerceptionSession")

async def run_session(duration_minutes: int = 5):
    sampler = VisualSampler(capture_dir="session_captures")
    engine = BehaviorSynthesisEngine()
    engine.capture_dir = "session_captures"
    
    start_time = datetime.now()
    end_time = start_time + timedelta(minutes=duration_minutes)
    
    print(f"\n--- 🧘 NSA Perception Session Started ({duration_minutes} min) ---")
    print(f"Start: {start_time.strftime('%H:%M:%S')}")
    print(f"End:   {end_time.strftime('%H:%M:%S')}")
    print("Please go about your work. Capturing every 15s...\n")

    capture_task = asyncio.create_task(sampler.run_loop(interval=15))
    
    try:
        # Progress indicator
        for i in range(duration_minutes * 2): # 30s increments
            remaining = (end_time - datetime.now()).total_seconds()
            if remaining <= 0: break
            print(f"⏳ Perception active... {int(remaining)}s remaining", end="\r")
            await asyncio.sleep(30)
            
        print("\n\n--- 🏁 Time Up! Starting Multimodal AI Synthesis ---")
        capture_task.cancel()
        
        # Give a small buffer for the last capture to finish
        await asyncio.sleep(2)
        
        # Perform synthesis for the specific window
        result = await engine.synthesize_window(minutes=duration_minutes + 1, delete_after=True)
        
        if result:
            print("\n" + "="*60)
            print("📜 BEHAVIORAL TRUTH REPORT (DUAL-AXIS ALIGNED)")
            print("="*60)
            
            # The new engine returns a dict with 'merged' key
            merged = result.get('merged', [])
            
            print(f"\n✨ SESSIONS: {len(merged)} identified blocks")
            
            print("\n📊 MERGED TIMELINE:")
            for entry in merged:
                smooth_tag = "[SMOOTHED] " if entry.get('is_smoothed') else ""
                print(f"- {entry.get('start')} | {entry.get('duration')}s | {entry.get('app')}")
                print(f"  Category: [{entry.get('inferred_category')}] Focus: {entry.get('focus_score')}")
                print(f"  Intent:   {smooth_tag}{entry.get('visual_context')}\n")
                
            print("\n" + "="*60 + "\n")
        else:
            print("❌ Synthesis failed. Check logs.")

    except Exception as e:
        logger.error(f"Session error: {e}")
    finally:
        capture_task.cancel()
        if os.path.exists("session_captures"):
            import shutil
            shutil.rmtree("session_captures")

if __name__ == "__main__":
    import sys
    duration = 5
    if len(sys.argv) > 1:
        try:
            duration = int(sys.argv[1])
        except ValueError:
            pass
    asyncio.run(run_session(duration))
