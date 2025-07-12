TEMP_DIR = "tmp/"

from captcha.image import ImageCaptcha
import uuid

class CaptchaGenerator:
    """Generates image-based CAPTCHA challenges and saves them to disk."""

    def __init__(self):
        """Initializes the CAPTCHA generator with predefined image dimensions."""
        self._image_captcha = ImageCaptcha(width=280, height=90)
        
    def _challenge(self) -> str:
        """Generates a random 6-character alphanumeric challenge string.

        Returns:
            str: A random string consisting of letters and digits.
        """
        import random
        import string
        characters = string.ascii_letters + string.digits
        return ''.join(random.choices(characters, k=6))
    
    def generate_captcha(self, challenge = None) -> tuple[str, str]:
        """Generates a CAPTCHA image and returns the file path and solution.

        Returns:
            tuple[str, str]: A tuple containing the file path to the image and the CAPTCHA solution string.
        """
        challenge = challenge or self._challenge()
        file_path = f"{TEMP_DIR}{uuid.uuid4()}.png"
        self._image_captcha.write(challenge, file_path)
        return file_path, challenge