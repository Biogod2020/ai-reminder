import asyncio
import os
import sys
import logging
import subprocess
import time
from datetime import datetime

# Ensure project root is in path
sys.path.append(os.getcwd())

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger("PermissionBootstrapper")

def open_settings(pane: str):
    subprocess.run(['open', f"x-apple.systempreferences:com.apple.preference.security?Privacy_{pane}"])

def check_accessibility():
    check_acc = 'tell application "System Events" to get name of first process whose frontmost is true'
    try:
        subprocess.check_output(['osascript', '-e', check_acc], stderr=subprocess.STDOUT)
        return True
    except subprocess.CalledProcessError:
        return False

def check_screen_recording():
    test_img = "perm_test.png"
    try:
        result = subprocess.run(['screencapture', '-x', test_img], capture_output=True, text=True)
        if result.returncode == 0 and os.path.exists(test_img):
            os.remove(test_img)
            return True
        return False
    except Exception:
        return False

def check_full_disk():
    db_path = os.path.expanduser("~/Library/Application Support/Knowledge/knowledgeC.db")
    try:
        subprocess.check_output(['ls', db_path], stderr=subprocess.STDOUT)
        return True
    except subprocess.CalledProcessError:
        return False

async def bootstrap_permission(name: str, check_func, pane_id: str):
    logger.info(f"--- 🛡️  Checking {name} ---")
    
    if check_func():
        logger.info(f"✅ {name}: ALREADY GRANTED")
        return True

    logger.warning(f"❌ {name}: DENIED")
    logger.info(f"👉 Opening System Settings: {name}...")
    open_settings(pane_id)
    
    print(f"\n[ACTION REQUIRED] Please toggle the switch for your terminal/IDE in the {name} list.")
    print("Watching for changes... (Press Ctrl+C to cancel)\n")
    
    while True:
        if check_func():
            print(f"\n✨ {name}: DETECTED PERMISSION GRANT!")
            logger.info(f"✅ {name}: GRANTED")
            return True
        
        # Some permissions require a full app restart to reflect in check_func
        # We remind the user every 15 seconds
        if int(time.time()) % 15 == 0:
            print(f"Still waiting for {name}... (If you already toggled it, you might need to RESTART this terminal session)")
            
        await asyncio.sleep(3)

async def main():
    print("\n" + "="*50)
    print("   🧘  Notion-Soul-Agent (NSA) Permission Bootstrapper")
    print("="*50)
    print("\nThis script will guide you through granting the 3 required macOS permissions.")
    
    # 1. Accessibility
    await bootstrap_permission("Accessibility", check_accessibility, "Accessibility")
    
    # 2. Screen Recording
    await bootstrap_permission("Screen Recording", check_screen_recording, "ScreenCapture")
    
    # 3. Full Disk Access
    await bootstrap_permission("Full Disk Access", check_full_disk, "AllFiles")

    print("\n" + "="*50)
    print("✨ ALL PERMISSIONS VERIFIED!")
    print("You are now ready to run the High-Fidelity Multimodal Stress Test.")
    print("\nCommand: .venv/bin/python scripts/stress_test_multimodal.py")
    print("="*50 + "\n")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Bootstrapper stopped by user. Please run again when ready.")
