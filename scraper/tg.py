#
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from loguru import logger
from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import Message

import settings
from data.minio_db import ImageDB
from data.redis_db import ImageRecord, MemDB
from extraction.ocr import OCRExtractor
from utils.funcs import ifnone


class TelegramScraper:
    """This class is used to scrape telegram channels, groups and chats."""

    def __init__(
            self,
            storage: ImageDB,
            index: MemDB,
    ):
        logger.info("Initializing scraper...")
        self.pool: ProcessPoolExecutor = ProcessPoolExecutor()
        self.storage: ImageDB = storage
        self.index: MemDB = index
        self.ocr: OCRExtractor = OCRExtractor()
        self.client: TelegramClient = TelegramClient(
            session=settings.SESSION_NAME,
            api_id=settings.API_ID,
            api_hash=settings.API_HASH,
        )

        if self.index.create_db():
            logger.info("Index database created for the first time.")

    def run(self, chat_id: str):
        self.client.start()
        self.client.loop.run_until_complete(self.scrape_messages(chat_id))
        self.client.run_until_disconnected()

    async def get_messages(
            self,
            chat_id: str,
            limit: int | None = 10000,
    ) -> list:
        logger.info(f"Getting messages from {chat_id}...")
        chat = await self.client.get_entity(chat_id)

        posts = await self.client(GetHistoryRequest(
            peer=chat,
            limit=limit,
            offset_date=None,
            offset_id=0,
            max_id=0,
            min_id=0,
            add_offset=0,
            hash=0),
        )
        logger.info(f"Got {len(posts.messages)} messages from {chat_id}.")

        return posts.messages

    async def process_message(self, message: Message, chat_slug: str):
        """Process message and save it to storage."""
        logger.info(f"Downloading image from {message.id}...")
        path = await self.download_img(message)
        logger.info(f"Saving image from {message.id}...")
        self.save_message(message, path, chat_slug=chat_slug)
        path.unlink()
        # res = self.pool.submit(self.save_message, message, path)
        # print(res.result())

    async def download_img(
            self,
            message: Message,
    ) -> Path:
        """Download image from message and return path to it."""
        p = Path(settings.TMP_DIR) / f"./images/{message.id}.jpg"

        path = await self.client.download_media(message.media, str(p.absolute()))
        return Path(path)

    def save_message(
            self,
            message: Message,
            path: Path,
            chat_slug: str,
    ):
        print(f"Saving img {path}")  # noqa

        self.storage.save_image(
            image=path.read_bytes(),
            chat_id=chat_slug,
            message_id=message.id,
            img_num=0,
            img_type="jpg",
        )

        self.index.add_record(ImageRecord(
            id=message.to_id.channel_id + message.id,
            message_id=message.id,
            chat=chat_slug,
            sender_id=ifnone(message.from_id, 0),
            dt=message.date,
            msg_text=ifnone(message.text, ""),
            ocr_rus=self.ocr.extract(path),
            ocr_eng="",
            semantic_data="",
            semantic_vector=[],
            reactions=[],
            comments=[],
            data_link=str(path.absolute()),
            post_link=f"https://t.me/{chat_slug}/{message.id}",
        ))

        logger.info(f"Saved message {message.id} to file {path}, storage and index.")

    async def scrape_messages(
            self,
            chat_slug: str,
    ):
        messages = await self.get_messages(chat_slug, limit=10000)

        for message in messages:
            logger.info(f"{message.id}: {message.text}")
            if message.photo:
                logger.info(f"Found image in {message.id}.")
                await self.process_message(message, chat_slug)
