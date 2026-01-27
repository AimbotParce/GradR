import asyncio
from pathlib import Path

from .database import create_tables, register_database
from .ui import GradingApp


async def main(db_path: Path):
    await register_database(db_path)
    await create_tables()
    app = GradingApp()
    await app.run_async()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Gradr - Manage grading projects and tasks from the terminal.")
    parser.add_argument("database", nargs="?", default="grading.db", help="Path to the SQLite database file.")
    args = parser.parse_args()

    db_path = Path(args.database)
    asyncio.run(main(db_path))
