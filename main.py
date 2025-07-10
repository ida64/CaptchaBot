"""Entry point for starting the service.

Starts the bot's main event loop.
"""

CAPTCHA_BOT_VERSION = "1.0.0-rc.1"
COPYRIGHT_NOTICE = "Copyright 2025 paging (GitHub: @ida64). All Rights Reserved."
COMMERCIAL_USE_NOTICE = "Commercial use of this software is prohibited without prior written permission from maintainer."

from loguru import logger

def print_notices():
    logger.info(f'ida64/CaptchaBot v{CAPTCHA_BOT_VERSION}')
    logger.warning(COPYRIGHT_NOTICE)
    logger.warning(COMMERCIAL_USE_NOTICE)

if __name__ == "__main__":
    print_notices()

    from discord_bot import run_bot
    import asyncio

    asyncio.run(run_bot())