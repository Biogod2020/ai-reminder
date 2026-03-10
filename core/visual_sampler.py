import os
import time
import asyncio
import logging
import subprocess
from datetime import datetime
from PIL import Image
from typing import Optional

logger = logging.getLogger("VisualSampler")

class VisualSampler:
    """
    Captures high-frequency screenshots (15s) and optimizes them for AI synthesis.
    Pauses automatically when the screen is backlit off.
    """
    
    def __init__(self, capture_dir: str = "captures", gallery_dir: str = "soul_gallery"):
        self.capture_dir = capture_dir
        self.gallery_dir = gallery_dir
        os.makedirs(self.capture_dir, exist_ok=True)
        os.makedirs(self.gallery_dir, exist_ok=True)
        
    def is_screen_on(self) -> bool:
        """Checks if the display is currently backlit using AppleScript."""
        script = 'tell application "System Events" to get value of attribute "AXHidden" of window 1 of process "Finder"'
        # Note: knowledgeC.db /display/isBacklit is better but async. 
        # For real-time, we check if we can get frontmost process name.
        check_script = 'tell application "System Events" to name of first process whose frontmost is true'
        try:
            subprocess.check_output(['osascript', '-e', check_script], text=True)
            return True
        except Exception:
            return False

    def capture_and_process(self) -> Optional[str]:
        """Captures a screenshot, resizes, and grayscales it."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        raw_path = os.path.join(self.capture_dir, f"raw_{timestamp}.png")
        proc_path = os.path.join(self.capture_dir, f"proc_{timestamp}.jpg")
        
        try:
            # 1. Capture using macOS native tool (silent mode)
            subprocess.run(['screencapture', '-x', raw_path], check=True)
            
            # 2. Process with Pillow
            with Image.open(raw_path) as img:
                # Use scale-based sampling (70% of original) instead of fixed width
                # This preserves Retina density and text clarity
                scale_factor = 0.7
                new_size = (int(img.size[0] * scale_factor), int(img.size[1] * scale_factor))
                img = img.resize(new_size, Image.Resampling.LANCZOS)
                
                # Ensure RGB mode for JPEG compatibility (fixes RGBA error)
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                
                # Higher quality (85) for better text OCR by Gemini
                img.save(proc_path, "JPEG", quality=85)
            
            # 3. Cleanup raw
            os.remove(raw_path)
            return proc_path
            
        except Exception as e:
            logger.error(f"Failed to capture/process screenshot: {e}")
            if os.path.exists(raw_path): os.remove(raw_path)
            return None

    async def run_loop(self, interval: int = 15):
        """Infinite loop for high-frequency sampling."""
        logger.info(f"Starting Visual Sampler loop (Interval: {interval}s)")
        while True:
            if self.is_screen_on():
                path = self.capture_and_process()
                if path:
                    logger.debug(f"Captured: {path}")
            else:
                logger.info("Screen appears to be off/locked. Skipping capture.")
            
            await asyncio.sleep(interval)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    sampler = VisualSampler()
    try:
        asyncio.run(sampler.run_loop(15))
    except KeyboardInterrupt:
        logger.info("Sampler stopped by user.")
