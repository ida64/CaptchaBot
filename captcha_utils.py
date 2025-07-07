TEMP_DIR = "tmp/"

from captcha.image import ImageCaptcha
import uuid

class CaptchaGenerator:
    def __init__(self):
        self._image_captcha = ImageCaptcha(width=280, height=90)
        
    def _challenge(self):
        import random
        import string
        characters = string.ascii_letters + string.digits
        return ''.join(random.choices(characters, k=6))
    
    def generate_captcha(self) -> tuple[str, str]:
        challenge = self._challenge()
        file_path = f"{TEMP_DIR}{uuid.uuid4()}.png"
        self._image_captcha.write(challenge, file_path)
        return file_path, challenge