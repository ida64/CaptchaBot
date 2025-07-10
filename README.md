# CaptchaBot: Anti-Spam and Raid Protection for Discord

![CaptchaBot Prompt](https://github.com/ida64/CaptchaBot/blob/main/img/prompt.png?raw=true)

CaptchaBot is a Python-based Discord bot designed to prevent spam and raids by requiring new users to solve a captcha before gaining access to your server.

## Features

- Easy-to-use captcha verification for new members
- Customizable captcha prompts and messages
- Automatic role assignment upon successful verification
- Protection against automated spam and raid attacks
- Simple setup and configuration

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/ida64/CaptchaBot.git
   cd CaptchaBot
   ```
2. Install the required dependencies:
   ```bash
    pip install -r requirements.txt
    ```
3. Perform the first run to generate the configuration file:
   ```bash
   python main.py
   ```
4. Edit the `config.json` file to set your bot token guild specific settings.