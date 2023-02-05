from pprint import pformat

import environ
from loguru import logger
from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest

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
    channel = await client.get_entity(chat_name)
    logger.info('Scraping chat %s', channel.title)

    posts = await client(GetHistoryRequest(
        peer=channel,
        limit=100,
        offset_date=None,
        offset_id=0,
        max_id=0,
        min_id=0,
        add_offset=0,
        hash=0))

    for message in posts.messages:
        logger.info(f'{message.id}: {message.text}')
        if message.photo:
            logger.info(f'File Name :{str(message.file.name)}')
            path = await client.download_media(message.media, "./images/mem")
            logger.info('File saved to', path)  # printed after download is done

    # logger.info(f'posts {pformat(posts[0])}')
    logger.info(f'posts {posts}')




def main():
    """Start the bot."""
    client.start()
    client.loop.run_until_complete(start())
    client.run_until_disconnected()


if __name__ == "__main__":
    main()
