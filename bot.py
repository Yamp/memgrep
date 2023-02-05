# import datetime
# import sqlite3
# from os import PathLike
import datetime
import sqlite3
from os import PathLike

import environ
import pytesseract
from PIL import Image
from loguru import logger
# import pytesseract
# from PIL import Image
# from loguru import logger
from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest

# from telethon.tl.functions.messages import GetHistoryRequest

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


def create_sqlite_table(name: PathLike) -> None:
    conn = sqlite3.connect(name)
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS posts
                 (
                 id INTEGER PRIMARY KEY UNIQUE NOT NULL,
                 msg_text text,
                 msg_date text,
                 file_name text,
                 file_path text
                 )
                 '''
              )
    conn.commit()
    conn.close()


def save_file_to_db(
        message: str,
        dt: datetime.datetime,
        filename: str,
        file_path: str,
        db_path: str = 'files.db',
):
    conn = sqlite3.connect(file_path)
    c = conn.cursor()
    c.execute("INSERT INTO files VALUES (?, ?, ?)", (
        message,
        dt,
        filename,
        file_path,
    ))
    conn.commit()
    conn.close()


def ocr_image(image_path: PathLike) -> str:
    """Extract text from image using OCR."""
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image, lang='rus')
    return text


async def start():
    """Main processing function."""
    channel = await client.get_entity(chat_name)
    logger.info('Scraping chat %s', channel.title)

    create_sqlite_table('files.db')

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
            # save_file_to_db(message.text, message.date, path, path)
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
