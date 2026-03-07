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
from core.truth_merger import DualAxisMerger

logger = logging.getLogger("SynthesisEngine")

class BehaviorSynthesisEngine:
    """
    Assembles visual streams and DB timelines into objective truth slices.
    Implements Dual-Axis Behavioral Architecture.
    """
    
    def __init__(self):
        self.adapter = GeminiAdapter()
        self.system_db = KnowledgeDB()
        self.shared_memory = SharedMemoryManager()
        self.merger = DualAxisMerger()
        self.capture_dir = "captures"
        self.gallery_dir = "soul_gallery"

    def _get_image_batch(self, start_dt: datetime, end_dt: datetime) -> List[Dict[str, Any]]:
        """Finds all processed images and their metadata within the time range."""
        images = []
        if not os.path.exists(self.capture_dir):
            return []
            
        for f in sorted(os.listdir(self.capture_dir)):
            if not f.startswith("proc_") or not f.endswith(".jpg"):
                continue
            try:
                # proc_20260308_004946.jpg
                parts = f.split("_")
                ts_str = f"{parts[1]}_{parts[2].split('.')[0]}"
                dt = datetime.strptime(ts_str, "%Y%m%d_%H%M%S")
                if start_dt <= dt <= end_dt:
                    images.append({
                        "path": os.path.join(self.capture_dir, f),
                        "timestamp": dt.isoformat() + "Z",
                        "filename": f
                    })
            except Exception:
                continue
        return images

    async def generate_intent_axis(self, image_metadata: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generates a standalone AI Intent Axis based on visual evidence."""
        if not image_metadata:
            return []

        image_data = []
        for item in image_metadata:
            try:
                image_data.append(Image.open(item["path"]))
            except Exception as e:
                logger.error(f"Failed to open {item['path']}: {e}")

        prompt = f"""
        TASK: GENERATE INDEPENDENT INTENT AXIS (Visual Logic Only)
        
        You are an expert behavior scientist. Analyze the provided sequence of screenshots.
        Ignore system logs for now; focus strictly on what the user is DOING visually.
        
        INSTRUCTIONS:
        1. For each significant cluster of images, identify the INTENT.
        2. CATEGORIES: [WORK], [LEISURE], [UTILITY], [AWAY].
        3. DETECT: Flow states, context switches, and cognitive intensity (0.0-1.0).
        4. KEY MOMENTS: Identify milestones or significant screen changes.
        
        OUTPUT FORMAT (JSON ONLY):
        {{
            "intent_stream": [
                {{
                    "timestamp": "ISO timestamp from metadata",
                    "category": "WORK",
                    "description": "Short description of screen content",
                    "focus_score": 0.9,
                    "is_key_moment": true/false
                }}
            ]
        }}
        """
        
        try:
            logger.info(f"Generating Intent Axis from {len(image_data)} images...")
            response_text = await self.adapter.generate_content(prompt, images=image_data, include_memory=False)
            
            clean_json = response_text.strip()
            if "```json" in clean_json: clean_json = clean_json.split("```json")[1].split("```")[0].strip()
            elif "```" in clean_json: clean_json = clean_json.split("```")[1].split("```")[0].strip()
            
            return json.loads(clean_json).get("intent_stream", [])
        except Exception as e:
            logger.error(f"Intent Axis generation failed: {e}")
            return []

    async def synthesize_window(self, minutes: int = 30, delete_after: bool = True):
        """Reconstructs behavioral truth using Dual-Axis Architecture."""
        end_dt = datetime.now()
        start_dt = end_dt - timedelta(minutes=minutes)
        
        logger.info(f"Synthesizing Dual-Axis window: {start_dt} to {end_dt}")
        
        # 1. Axis A: System Objective Axis
        system_timeline = self.system_db.get_timeline(start_dt, end_dt)
        
        # 2. Axis B: AI Visual Intent Axis
        image_metadata = self._get_image_batch(start_dt, end_dt)
        intent_stream = await self.generate_intent_axis(image_metadata)
        
        # 3. Truth Merger (Logic now Formalized)
        merged_timeline = self.merger.merge(system_timeline, intent_stream)
        
        result = {
            "window_id": f"window_{end_dt.strftime('%Y%m%d_%H%M')}",
            "start_time": start_dt.isoformat() + "Z",
            "end_time": end_dt.isoformat() + "Z",
            "layers": {
                "system_axis": system_timeline,
                "ai_axis": intent_stream,
                "merged_timeline": merged_timeline
            }
        }

        # 4. Handle Key Moments & Gallery
        for intent in intent_stream:
            if intent.get("is_key_moment"):
                ts = intent["timestamp"].replace("-", "").replace(":", "").replace("T", "_").split("Z")[0]
                # Try to find file matching this timestamp
                for img in image_metadata:
                    if ts in img["filename"]:
                        dest = os.path.join(self.gallery_dir, img["filename"])
                        shutil.copy2(img["path"], dest)
                        logger.info(f"Saved Key Moment to Soul Gallery: {dest}")

        # 5. Persistent Storage (SQLite)
        from sqlalchemy import create_engine, text
        engine_db = create_engine("sqlite:///notion_soul.db")
        with engine_db.connect() as conn:
            stmt = text("""
                INSERT INTO omni_behavior_log (window_id, start_time, end_time, layers_json, updated_at)
                VALUES (:wid, :start, :end, :layers, :upd)
                ON CONFLICT(window_id) DO UPDATE SET
                    layers_json = excluded.layers_json,
                    updated_at = excluded.updated_at
            """)
            conn.execute(stmt, {
                "wid": result["window_id"],
                "start": start_dt,
                "end": end_dt,
                "layers": json.dumps(result["layers"]),
                "upd": datetime.now(timezone.utc)
            })
            conn.commit()

        # 6. Cleanup
        if delete_after:
            for img in image_metadata:
                try: os.remove(img["path"])
                except Exception: pass
            logger.info(f"Cleaned up {len(image_metadata)} snapshots.")
            
        return result

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    engine = BehaviorSynthesisEngine()
    asyncio.run(engine.synthesize_window(minutes=30, delete_after=False))
