#!/usr/bin/env python3
import sys

sys.path.extend([".", "..", "../.."])

import fire
from loguru import logger

from data.minio_db import MinioDB
from data.redis_db import RedisDB
from scraper.tg import TelegramScraper


def index(
        chat_id: str,
):
    logger.info("Initializing storage...")
    storage = MinioDB()
    logger.info("Initializing index...")
    index = RedisDB()
    logger.info("Initializing scraper...")
    scraper = TelegramScraper(storage, index)

    logger.info("Scraping messages...")
    scraper.run(chat_id)
    logger.info("Done!")

if __name__ == "__main__":
    fire.Fire(index)
