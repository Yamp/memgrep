import logging

import environ
from loguru import logger
from telethon import TelegramClient

logging.basicConfig(
    format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
    level=logging.WARNING
)

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)
# reading .env file
environ.Env.read_env()
# False if not in os.environ
DEBUG = env('DEBUG')


# These example values won't work. You must get your own api_id and
# api_hash from https://my.telegram.org, under API Development.
api_id = env('API_ID')
api_hash = env('API_HASH')
session_name = env('SESSION_NAME')
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
