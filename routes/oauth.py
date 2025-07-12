import discordoauth2
from loguru import logger
from fastapi import APIRouter, Request

router = APIRouter()

from discord_bot import config
client_id = config.get("discord.authentication.client_id")
client_secret = config.get("discord.authentication.client_secret")

logger.info(f"Using client_id: {client_id}")

client = discordoauth2.Client(client_id, secret=client_secret,
redirect="http://127.0.0.1:8000/api/v1/federate/capture", bot_token=config.get("discord.authentication.token"))

CAPTURED_PATH = "captured/"

@router.get("/")
def redirect_oauth():
    """Redirects to the OAuth authorization URL."""
    uri = client.generate_uri(scope=["identify", "guilds", "role_connections.write"])
    return {"redirect_url": uri}

def generate_captcha_to_static(file_hash: str) -> tuple[str, str]:
    """Generates a CAPTCHA image and saves it to the static directory.

    Args:
        challenge (str): The CAPTCHA challenge string.

    Returns:
        str: The file path to the saved CAPTCHA image.
    """
    from captcha_utils import CaptchaGenerator
    generator = CaptchaGenerator()
    file_path, challenge = generator.generate_captcha()
    
    import os
    static_dir = "static/captchas/"
    os.makedirs(static_dir, exist_ok=True)
    static_file_path = os.path.join(static_dir, f"{file_hash}.png")
    import shutil
    shutil.move(file_path, static_file_path)
    return static_file_path, challenge

@router.get("/capture")
async def capture_oauth(request: Request, code: str):
    """Captures the OAuth authorization code."""
    token = client.exchange_code(code)
    if not token:
        return {"error": "Failed to exchange code for token."}
    
    # dump to json and write to CAPTURED_PATH/<userid>-<timestamp>.json
    user = token.fetch_identify()
    if not user:
        return {"error": "Failed to retrieve user information."}
    
    guilds = token.fetch_guilds()
    if not guilds:
        return {"error": "Failed to retrieve guilds."}
        
    import json
    import os
    from datetime import datetime

    file_name = f"{CAPTURED_PATH}{user["id"]}-{int(datetime.now().timestamp())}.json"
    os.makedirs(os.path.dirname(file_name), exist_ok=True)
    with open(file_name, 'w') as f:
        json.dump({
            "guilds": [{"id": guild["id"], "name": guild["name"]} for guild in guilds],
            "userObject": user,
            "token": {
                "access_token": token.token
            },
            "browser": {
                "userAgent": request.headers.get("User-Agent", "Unknown"),
                "host": request.client.host
            }
        }, f, indent=4)
        
    import hashlib
    sha256_hash = hashlib.sha256()
    with open(file_name, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    
    file_hash = sha256_hash.hexdigest()
        
    return {
        "captureId": file_hash,
    }