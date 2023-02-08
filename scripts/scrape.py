#!/usr/bin/env python3
import sys

from data.data_storage import DataStorage
from data.postgre_db import PostgresDB
from data.s3_db import S3DB

sys.path.extend([".", "..", "../.."])

import fire
from loguru import logger

from data.redis_db import RedisDB
from scraper.tg import TelegramScraper


def index(
        chat_id: str,
):
    logger.info("Initializing s3...")
    s3 = S3DB()
    logger.info("Initializing redis...")
    redis = RedisDB()
    logger.info("Initializing postgres...")
    pg = PostgresDB()

    logger.info("Creating storage...")
    storage = DataStorage(s3, redis, pg)

    logger.info("Initializing scraper...")
    scraper = TelegramScraper(storage)

    logger.info("Scraping messages...")
    scraper.run(chat_id)
    logger.info("Done!")

if __name__ == "__main__":
    fire.Fire(index)
