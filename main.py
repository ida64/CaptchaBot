"""Entry point for starting the service.

Loads environment variables and runs the bot's main event loop.
"""

from dotenv import load_dotenv

if __name__ == "__main__":
    load_dotenv()

    from discord_bot import run_bot
    import asyncio

    asyncio.run(run_bot())