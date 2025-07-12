"""Entry point for starting the service.

Starts the bot's main event loop.
"""

CAPTCHA_BOT_VERSION = "1.0.0-rc.1"
COPYRIGHT_NOTICE = "Copyright 2025 paging (GitHub: @ida64). All Rights Reserved."
COMMERCIAL_USE_NOTICE = "Commercial use of this software is prohibited without prior written permission from maintainer."

import asyncio
from loguru import logger

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn

from routes import oauth

app = FastAPI()

app.include_router(oauth.router, prefix="/api/v1/federate", tags=["Federate OAuth"])
app.mount("/static", StaticFiles(directory="static"), name="static")

def print_notices():
    logger.info(f'ida64/CaptchaBot v{CAPTCHA_BOT_VERSION}')
    logger.warning(COPYRIGHT_NOTICE)
    logger.warning(COMMERCIAL_USE_NOTICE)

async def startup(): 
    from discord_bot import run_bot
    bot_task = asyncio.create_task(run_bot())
    api_task = asyncio.create_task(start_api())
    await asyncio.gather(bot_task, api_task)

async def start_api():
    config = uvicorn.Config("main:app", host="0.0.0.0", port=8000, log_level="info", reload=False)
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    print_notices()

    try:
        asyncio.run(startup())
    except KeyboardInterrupt:
        logger.info("Shutdown requested by user.")
    except Exception as e:
        logger.exception(f"Unhandled error occurred: {e}")
