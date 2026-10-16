import asyncio
from pathlib import Path

from japan import Orchestrator


async def main():
    async with Orchestrator(output=Path("japan_tariffs")) as orchestrator:
        await orchestrator.download()

if __name__ == "__main__":
    asyncio.run(main())
