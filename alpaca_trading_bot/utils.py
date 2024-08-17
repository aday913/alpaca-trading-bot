import logging
import os

import discord_webhook
from dotenv import load_dotenv

log = logging.getLogger(__name__)


def send_discord_message(url: str, message: str):
    """
    Send a message to a Discord webhook

    :param url: Discord webhook URL
    :param message: Message to send
    """
    log.info(f"Connecting to Discord webhook at {url}")
    webhook = discord_webhook.DiscordWebhook(url=url)

    log.info(f"Sending message: {message}")
    webhook.content = message
    response = webhook.execute()

    if response.status_code != 200:
        log.error(f"Failed to send message: {response}")
        return False

    log.info(f"Message sent: {response}")
    return True


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)

    # Load API keys from .env file
    load_dotenv()

    send_discord_message(os.getenv("DISCORD_WEBHOOK_URL"), "Hello, world!")
