import json
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

logger = logging.getLogger("TruthMerger")

class DualAxisMerger:
    """
    Overlays the AI Intent Axis (Visual) onto the System Objective Axis (App Usage).
    Detects conflicts and calculates high-fidelity metrics.
    """
    
    def merge(self, system_axis: List[Dict[str, Any]], ai_axis: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Merges two axes into a single unified behavioral timeline.
        """
        if not system_axis:
            return [{"start": a["timestamp"], "app": "Unknown", "inferred_category": a["category"], "visual_context": a["description"]} for a in ai_axis]

        merged_timeline = []
        
        for block in system_axis:
            block_start = block["start"]
            
            relevant_intents = []
            for intent in ai_axis:
                if self._is_within(intent["timestamp"], block):
                    relevant_intents.append(intent)
            
            if relevant_intents:
                category = self._get_dominant_category(relevant_intents)
                description = " | ".join(list(set([i["description"] for i in relevant_intents])))
                focus_score = sum([i.get("focus_score", 0.5) for i in relevant_intents]) / len(relevant_intents)
            else:
                category = "UNCATEGORIZED"
                description = "No visual data for this block."
                focus_score = 0.0

            merged_timeline.append({
                "start": block_start,
                "duration": block["duration_seconds"],
                "app": block["app"],
                "inferred_category": category,
                "visual_context": description,
                "focus_score": round(focus_score, 2),
                "conflict_detected": self._check_conflict(block["app"], category)
            })
            
        return merged_timeline

    def _is_within(self, timestamp: str, block: Dict[str, Any]) -> bool:
        # Simple string comparison works for ISO timestamps in sequential order
        return block["start"] <= timestamp

    def _get_dominant_category(self, intents: List[Dict[str, Any]]) -> str:
        from collections import Counter
        cats = [i["category"] for i in intents]
        return Counter(cats).most_common(1)[0][0]

    def _check_conflict(self, app_name: str, category: str) -> bool:
        """Flag if a known 'Work' app is being used for 'Leisure' or vice versa."""
        work_apps = ["Xcode", "PyCharm", "VS Code", "Terminal", "Iterm2", "Linear", "Notion", "Chrome", "Safari", "Arc"]
        leisure_apps = ["Spotify", "Bilibili", "YouTube", "Netflix", "WeChat"] # WeChat moments is leisure
        
        if app_name in work_apps and category == "LEISURE":
            return True
        if app_name in leisure_apps and category == "WORK":
            # This is interesting: using Spotify for Work? Maybe focus music?
            # For now only flag high-signal conflicts.
            return False
        return False
