import asyncio

from .database import create_tables
from .ui import GradingApp


async def main():
    await create_tables()
    app = GradingApp()
    await app.run_async()


if __name__ == "__main__":
    asyncio.run(main())
