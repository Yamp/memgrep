#
from pathlib import Path

from loguru import logger
from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import Channel, Message

import settings
from data.data_storage import DataStorage
from data.redis_db import ImageRecord
from entities.message import PImage, PMessage
from extraction.ocr import OCRExtractor
from utils.funcs import ifnone


class TelegramScraper:
    """This class is used to scrape telegram channels, groups and chats."""

    def __init__(
            self,
            storage: DataStorage,
    ):
        logger.info("Initializing scraper...")
        self.storage: DataStorage = storage
        self.ocr: OCRExtractor = OCRExtractor()
        self.client: TelegramClient = TelegramClient(
            session=settings.TG_SESSION_NAME,
            api_id=settings.TG_API_ID,
            api_hash=settings.TG_API_HASH,
        )

    def run(self, chat_id: str):
        self.client.start()
        self.client.loop.run_until_complete(self.scrape_messages(chat_id))
        self.client.run_until_disconnected()

    async def get_messages(
            self,
            chat_id: str,
            limit: int | None = 10000,
            chunk_size: int = 100,
    ) -> list[Message]:
        logger.info(f"Getting messages from {chat_id}...")
        chat = await self.client.get_entity(chat_id)

        messages = []
        offset = 0
        for i in range(limit // chunk_size + 1):
            logger.info(f"Getting {chunk_size} messages from {chat_id}...")
            posts = await self.client(GetHistoryRequest(
                peer=chat,
                limit=chunk_size,
                offset_date=None,
                offset_id=0,
                max_id=0,
                min_id=0,
                add_offset=offset,
                hash=0),
            )
            new_messages = list(posts.messages)
            offset += len(new_messages)
            messages.extend(new_messages)

            if not new_messages:
                logger.info(f"Finished getting messages from {chat_id} in {i} iterations.")
                break

        logger.info(f"Got total of {len(messages)} messages from {chat_id}.")

        return messages

    async def process_message(self, chat_slug: str, message: Message):
        """Process message and save it to storage."""
        img = self.search_db(chat_slug, message)
        if img is not None:
            logger.info(f"Image from {message.id} already exists in database.")
            return

        logger.info(f"Downloading image from {message.id}...")
        path = await self.download_img(message)
        if path is None:
            return

        logger.info(f"Saving image from {message.id}...")
        self.save_message(message, path, chat_slug=chat_slug)
        path.unlink()
        # res = self.pool.submit(self.save_message, message, path)
        # print(res.result())

    async def download_img(
            self,
            message: Message,
    ) -> Path | None:
        """Download image from message and return path to it."""
        p = Path(settings.TMP_DIR) / f"./images/{message.id}.jpg"

        path = await self.client.download_media(message, file=str(p.absolute()))
        if path is None:
            logger.warning(f"Failed to download image from {message.id}.")
        path = await self.client.download_media(message.photo, file=str(p.absolute()))
        if path is None:
            logger.warning(f"Failed to download photo from {message.id}.")
            return None

        return Path(path)

    def search_db(
            self,
            img: PImage,
    ) -> bytes | None:
        return self.storage.download_image(img)

    def save_message(
            self,
            message: Message,
            path: Path,
            chat_slug: str,
    ):
        print(f"Saving img {path}")  # noqa

        img = PImage(
            id=message.to_id.channel_id + message.id,
            data=path.read_bytes(),
            extension=path.suffix,
            num=0,
        )

        self.storage.upload_image(img)

        self.storage.index.add_record(ImageRecord(
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
        chan: Channel = await self.client.get_entity(chat_slug)

        msgs = [PMessage.from_tg(m, chan) for m in messages]
        self.storage.save_messages(msgs=msgs)
        logger.info(f"Saved {len(msgs)} messages to storage.")

    # async def scrape_images(
    #         self,
    #         chat_slug: str,
    # ):
    #     for message in messages:
    #         logger.info(f"{message.id}: {message.text}")
    #         if message.photo:
    #             logger.info(f"Found image in {message.id}.")
    #             await self.process_message(chat_slug, message)
