import asyncio
import sys
import os

# Ensure project root is in path
sys.path.append(os.getcwd())

from core.initialization import InitializationManager

async def main():
    manager = InitializationManager()
    await manager.run_cli_session()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nInitialization cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nAn error occurred during initialization: {e}")
        sys.exit(1)
