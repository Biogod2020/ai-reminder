import subprocess
import asyncio
import logging
from typing import Dict, Optional
from core.memory import SharedMemoryManager

logger = logging.getLogger("SystemMonitor")

class MacOSMonitor:
    """Monitors macOS system metrics via AppleScript to trigger memory updates."""
    
    def __init__(self):
        self.shared_memory = SharedMemoryManager()
        self.last_app = None

    def get_active_app_info(self) -> Dict[str, str]:
        """Returns the name and window title of the frontmost application."""
        script = '''
            tell application "System Events"
                set frontmostProcess to first process whose frontmost is true
                set processName to name of frontmostProcess
                tell frontmostProcess
                    if (count windows) > 0 then
                        set windowTitle to name of first window
                    else
                        set windowTitle to "No active window"
                    end if
                end tell
                return processName & "|||" & windowTitle
            end tell
        '''
        try:
            result = subprocess.check_output(['osascript', '-e', script], text=True).strip()
            parts = result.split("|||")
            return {
                "app_name": parts[0],
                "window_title": parts[1] if len(parts) > 1 else "Unknown"
            }
        except Exception as e:
            logger.error(f"Failed to get active app info: {e}")
            return {"app_name": "Unknown", "window_title": "Unknown"}

    async def monitor_loop(self, interval: int = 60):
        """Periodically checks system state and updates short-term memory."""
        logger.info(f"Starting system monitor loop (interval: {interval}s)")
        while True:
            try:
                info = self.get_active_app_info()
                app_name = info["app_name"]
                
                # Only log/update if the app changed to avoid noise
                if app_name != self.last_app:
                    logger.info(f"System focus shifted to: {app_name}")
                    await self.shared_memory.add(
                        content=f"User is currently using {app_name} (Window: {info['window_title']})",
                        metadata={"scope": "session", "type": "app_focus"}
                    )
                    self.last_app = app_name
                
            except Exception as e:
                logger.error(f"Error in monitor loop: {e}")
            
            await asyncio.sleep(interval)

if __name__ == "__main__":
    monitor = MacOSMonitor()
    asyncio.run(monitor.monitor_loop(10))
