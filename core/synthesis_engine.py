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
    Implements the true DUAL-AXIS behavioral architecture.
    Axis A: System Objective (KnowledgeDB)
    Axis B: AI Visual Intent (Gemini Vision)
    """
    
    def __init__(self):
        self.adapter = GeminiAdapter()
        self.system_db = KnowledgeDB()
        self.shared_memory = SharedMemoryManager()
        self.merger = DualAxisMerger()
        self.capture_dir = "captures"
        self.gallery_dir = "soul_gallery"

    def _get_image_batch(self, start_dt: datetime, end_dt: datetime) -> List[Dict[str, Any]]:
        image_paths = []
        if not os.path.exists(self.capture_dir):
            return []
        for f in sorted(os.listdir(self.capture_dir)):
            if not f.startswith("proc_") or not f.endswith(".jpg"): continue
            try:
                parts = f.split("_")
                ts_str = f"{parts[1]}_{parts[2].split('.')[0]}"
                dt = datetime.strptime(ts_str, "%Y%m%d_%H%M%S")
                if start_dt <= dt <= end_dt:
                    image_paths.append({"path": os.path.join(self.capture_dir, f), "timestamp": dt.isoformat() + "Z", "filename": f})
            except Exception: continue
        return image_paths

    async def synthesize_window(self, minutes: int = 30, delete_after: bool = True):
        end_dt = datetime.now()
        start_dt = end_dt - timedelta(minutes=minutes)
        logger.info(f"Synthesizing window (True Dual-Axis): {start_dt} to {end_dt}")
        
        # 1. Axis A: System Objective Axis (Immutable Truth from OS)
        system_timeline = self.system_db.get_timeline(start_dt, end_dt)
        
        # 2. Axis B: AI Visual Intent Axis (Pure Visual Inference)
        image_metadata = self._get_image_batch(start_dt, end_dt)
        if not image_metadata:
            logger.info("No images found. Skipping visual synthesis.")
            return

        image_data = [Image.open(img["path"]) for img in image_metadata]

        # SOTA Intent Prompt: Focus strictly on Visual Intent
        prompt = f"""
        TASK: GENERATE INDEPENDENT VISUAL INTENT AXIS
        
        You are observing a user's screen snapshots. 
        Analyze the sequence and reconstruct the INTENT axis.
        
        INSTRUCTIONS:
        - DO NOT merge or aggregate events to match app logs.
        - FOR EACH SNAPSHOT (or small cluster), determine:
          1. CATEGORY: [WORK], [LEISURE], [UTILITY], [AWAY].
          2. SEMANTIC CONTEXT: What is actually happening? (e.g., "Debugging Python", "Browsing social media").
          3. FOCUS SCORE: 0.0 - 1.0.
        - REFERENCE LOG: {json.dumps(system_timeline[:10])} (Use this ONLY to identify apps).
        
        OUTPUT FORMAT (JSON ONLY):
        {{
            "visual_intent_stream": [
                {{
                    "timestamp": "ISO timestamp of the image",
                    "category": "WORK",
                    "description": "...",
                    "focus_score": 0.9,
                    "is_key_moment": true/false
                }}
            ]
        }}
        """
        
        try:
            logger.info(f"Requesting Intent Axis for {len(image_data)} snapshots...")
            response_text = await self.adapter.generate_content(prompt, images=image_data, include_memory=False)
            
            clean_json = response_text.strip()
            if "```json" in clean_json: clean_json = clean_json.split("```json")[1].split("```")[0].strip()
            elif "```" in clean_json: clean_json = clean_json.split("```")[1].split("```")[0].strip()
            
            ai_intent_axis = json.loads(clean_json).get("visual_intent_stream", [])
            
            # 3. Local Truth Merger: Point-to-Point Overlay
            merged_timeline = self.merger.merge(system_timeline, ai_intent_axis)
            
            # 4. Storage
            from sqlalchemy import create_engine, text
            engine_db = create_engine("sqlite:///notion_soul.db")
            with engine_db.connect() as conn:
                stmt = text("""
                    INSERT INTO omni_behavior_log (window_id, start_time, end_time, layers_json, updated_at)
                    VALUES (:wid, :start, :end, :layers, :upd)
                    ON CONFLICT(window_id) DO UPDATE SET layers_json = excluded.layers_json, updated_at = excluded.updated_at
                """)
                conn.execute(stmt, {
                    "wid": f"window_{end_dt.strftime('%Y%m%d_%H%M')}",
                    "start": start_dt, "end": end_dt,
                    "layers": json.dumps({
                        "system_axis": system_timeline,
                        "ai_axis": ai_intent_axis,
                        "merged_timeline": merged_timeline
                    }),
                    "upd": datetime.now(timezone.utc)
                })
                conn.commit()

            if delete_after:
                for img in image_metadata: os.remove(img["path"])
            
            return {"merged": merged_timeline, "ai_axis": ai_intent_axis}
            
        except Exception as e:
            logger.error(f"Dual-Axis Synthesis failed: {e}")
            return None

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    engine = BehaviorSynthesisEngine()
    asyncio.run(engine.synthesize_window(minutes=60, delete_after=False))
