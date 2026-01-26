import asyncio

from .database import create_tables


def main():
    asyncio.run(create_tables())


if __name__ == "__main__":
    main()
