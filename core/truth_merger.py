import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

logger = logging.getLogger("TruthMerger")


class DualAxisMerger:
    """
    Overlays the AI Intent Axis (Visual) onto the System Objective Axis (App Usage).
    Ensures robust fallbacks even when system logs are missing or delayed.
    """
    
    def merge(
        self, 
        system_axis: List[Dict[str, Any]], 
        ai_axis: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Merges two axes into a single unified behavioral timeline.
        """
        # If no system data, construct a best-effort timeline from AI visual axis
        if not system_axis:
            logger.warning("System Axis is empty. Constructing visual-only timeline.")
            return [
                {
                    "start": a["timestamp"], 
                    "duration": 15, # Default to sampling interval
                    "app": "Observed via Vision", 
                    "inferred_category": a["category"], 
                    "visual_context": a["description"],
                    "focus_score": a.get("focus_score", 0.5),
                    "is_smoothed": False
                } for a in ai_axis
            ]

        merged_timeline = []
        
        for block in system_axis:
            try:
                b_start_str = block["start"].split("+")[0]
                b_start = datetime.fromisoformat(b_start_str)
                b_end_ts = b_start.timestamp() + block["duration_seconds"]
            except Exception as e:
                logger.error(f"Failed to parse system block timestamp: {e}")
                continue
            
            relevant_intents = []
            for intent in ai_axis:
                try:
                    i_ts_str = intent["timestamp"].replace("Z", "").split("+")[0]
                    i_ts = datetime.fromisoformat(i_ts_str).timestamp()
                    if b_start.timestamp() <= i_ts <= b_end_ts:
                        relevant_intents.append(intent)
                except Exception:
                    continue
            
            if relevant_intents:
                category = self._get_dominant_category(relevant_intents)
                description = " | ".join(
                    list(set([i["description"] for i in relevant_intents]))
                )
                focus_score = sum(
                    [i.get("focus_score", 0.5) for i in relevant_intents]
                ) / len(relevant_intents)
                is_smoothed = False
            else:
                category = "UNCATEGORIZED"
                description = "No direct visual data for this block."
                focus_score = 0.0
                is_smoothed = True

            merged_timeline.append({
                "start": block["start"],
                "duration": block["duration_seconds"],
                "app": block["app"],
                "inferred_category": category,
                "visual_context": description,
                "focus_score": round(focus_score, 2),
                "is_smoothed": is_smoothed
            })
            
        return self._apply_inertia(merged_timeline)

    def _apply_inertia(self, timeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        for i in range(len(timeline)):
            if timeline[i]["inferred_category"] == "UNCATEGORIZED" and timeline[i]["duration"] < 60:
                if i > 0 and timeline[i-1]["inferred_category"] != "UNCATEGORIZED":
                    timeline[i]["inferred_category"] = timeline[i-1]["inferred_category"]
                    timeline[i]["visual_context"] = f"[Inferred] {timeline[i-1]['visual_context']}"
                    timeline[i]["focus_score"] = timeline[i-1]["focus_score"]
        return timeline

    def _get_dominant_category(self, intents: List[Dict[str, Any]]) -> str:
        from collections import Counter
        cats = [i["category"] for i in intents]
        return Counter(cats).most_common(1)[0][0]

    def normalize_timestamps(self, timeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        for entry in timeline:
            if "start" in entry and isinstance(entry["start"], str):
                entry["start"] = entry["start"].replace("Z", "+00:00")
        return timeline
