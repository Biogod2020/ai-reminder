import os
import asyncio
import logging
import json
import shutil
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional
from PIL import Image
from core.adapter import GeminiAdapter
from core.system_db import KnowledgeDB
from core.memory import SharedMemoryManager

logger = logging.getLogger("SynthesisEngine")

class BehaviorSynthesisEngine:
    """
    Assembles visual streams and DB timelines into objective truth slices.
    Categorizes behavior and identifies key moments for the soul.
    """
    
    def __init__(self):
        self.adapter = GeminiAdapter()
        self.system_db = KnowledgeDB()
        self.shared_memory = SharedMemoryManager()
        self.capture_dir = "captures"
        self.gallery_dir = "soul_gallery"

    def _get_image_batch(self, start_dt: datetime, end_dt: datetime) -> List[str]:
        """Finds all processed images within the time range."""
        image_paths = []
        if not os.path.exists(self.capture_dir):
            return []
            
        for f in sorted(os.listdir(self.capture_dir)):
            if not f.startswith("proc_") or not f.endswith(".jpg"):
                continue
            try:
                # proc_20260307_204946.jpg
                parts = f.split("_")
                ts_str = f"{parts[1]}_{parts[2].split('.')[0]}"
                dt = datetime.strptime(ts_str, "%Y%m%d_%H%M%S")
                # Simple naive comparison for now
                if start_dt <= dt <= end_dt:
                    image_paths.append(os.path.join(self.capture_dir, f))
            except Exception:
                continue
        return image_paths

    async def synthesize_window(self, minutes: int = 30, delete_after: bool = True):
        """Processes the last X minutes of behavior and cleans up assets."""
        end_dt = datetime.now()
        start_dt = end_dt - timedelta(minutes=minutes)
        
        logger.info(f"Starting synthesis for window: {start_dt} to {end_dt}")
        
        # 1. Fetch Timeline
        timeline = self.system_db.get_timeline(start_dt, end_dt)
        timeline_str = "\n".join([f"[{e['start']}] {e['app']} ({e['duration_seconds']}s)" for e in timeline])
        
        # 2. Fetch Images
        image_paths = self._get_image_batch(start_dt, end_dt)
        if not image_paths and not timeline:
            logger.info("No data found in window. Skipping synthesis.")
            return

        # Prepare images for Gemini
        image_data = []
        for path in image_paths:
            try:
                img = Image.open(path)
                image_data.append(img)
            except Exception as e:
                logger.error(f"Failed to open {path}: {e}")

        # 3. SOTA Synthesis Prompt
        prompt = f"""
        TASK: RECONSTRUCT BEHAVIORAL TRUTH (Window: {minutes} minutes)
        
        INPUT DATA:
        - TIMELINE (knowledgeC.db):
        {timeline_str if timeline_str else "No app usage recorded in DB."}
        
        - VISUAL STREAM: {len(image_paths)} snapshots provided.
        
        INSTRUCTIONS:
        1. CATEGORIZE: For each significant time block, assign a category: [WORK], [LEISURE], [UTILITY], [AWAY].
        2. FLOW ANALYSIS: Detect 'Flow States' (high focus, single task) vs 'Fragmentation' (heavy switching).
        3. KEY MOMENTS: Identify 1-2 'Key Moments' by identifying the visual index (e.g., "Image 5") or timestamp.
        4. REASONING: Explain WHY you categorized things this way.
        
        OUTPUT FORMAT (JSON ONLY):
        {{
            "summary": "High level summary of focus and productivity.",
            "timeline": [
                {{"start": "ISO", "end": "ISO", "app": "Name", "category": "Work/Leisure/...", "score": 0.0-1.0, "reasoning": "..."}}
            ],
            "key_moments": [
                {{"timestamp": "YYYYMMDD_HHMMSS", "description": "...", "importance": "high"}}
            ]
        }}
        """
        
        try:
            logger.info(f"Sending {len(image_data)} images to Gemini for synthesis...")
            response_text = await self.adapter.generate_content(prompt, images=image_data, include_memory=False)
            
            # Clean JSON
            clean_json = response_text.strip()
            if "```json" in clean_json: clean_json = clean_json.split("```json")[1].split("```")[0].strip()
            elif "```" in clean_json: clean_json = clean_json.split("```")[1].split("```")[0].strip()
            
            result = json.loads(clean_json)
            
            # 4. Handle Key Moments (Move to gallery)
            key_moment_ts = [km["timestamp"] for km in result.get("key_moments", [])]
            for ts in key_moment_ts:
                # Find the corresponding file
                for path in image_paths:
                    if ts in path:
                        dest = os.path.join(self.gallery_dir, os.path.basename(path))
                        shutil.copy2(path, dest)
                        logger.info(f"Saved Key Moment: {dest}")

            # 5. Store result in SQLite
            await self.shared_memory.add(
                content=result,
                metadata={"scope": "truth_slice", "window_minutes": minutes}
            )
            
            # 6. Cleanup raw captures
            if delete_after:
                for path in image_paths:
                    try:
                        os.remove(path)
                    except Exception:
                        pass
                logger.info(f"Cleaned up {len(image_paths)} temporary screenshots.")
                
            return result
            
        except Exception as e:
            logger.error(f"Synthesis failed: {e}")
            return None

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    engine = BehaviorSynthesisEngine()
    # To test, we'd need some images in captures/
    asyncio.run(engine.synthesize_window(30, delete_after=False))
