"""Entry point for starting the service.

Starts the bot's main event loop.
"""

if __name__ == "__main__":
    from discord_bot import run_bot
    import asyncio

    asyncio.run(run_bot())