import logging

from loguru import logger
from telethon import TelegramClient

logging.basicConfig(
    format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
    level=logging.WARNING
)

# These example values won't work. You must get your own api_id and
# api_hash from https://my.telegram.org, under API Development.
api_id = 109107
api_hash = "bea74e3b2fb952d3f2bc1f4cfee3ad23"
session_name = "simitrius.session"
chat_name = "memes161"

client = TelegramClient(session=session_name, api_id=api_id, api_hash=api_hash)

search_words = []


async def start():
    """Main processing function."""
    global receiver
    receiver = await client.get_entity(chat_name)
    logger.info('Scraping chat %s', receiver.title)


def main():
    """Start the bot."""
    client.start()
    client.loop.run_until_complete(start())
    client.run_until_disconnected()


if __name__ == "__main__":
    main()
