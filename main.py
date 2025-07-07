from loguru import logger
from dotenv import load_dotenv

if __name__ == "__main__":
    load_dotenv()

    from discord_bot import run_bot
    import asyncio
    asyncio.run(run_bot())
    logger.info("Bot has stopped.")