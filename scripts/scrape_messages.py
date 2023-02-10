#!/usr/bin/env python3
import fire

from data.data_storage import DataStorage
from data.pg.postgre_db import PostgresDB
from data.redis_db import RedisDB
from data.s3_db import S3DB
from scraper.tg import TelegramScraper


def scrape(chat_username: str):
    s3 = S3DB()
    redis = RedisDB()
    pg = PostgresDB()
    storage = DataStorage(s3, redis, pg)
    s = TelegramScraper(storage)

    # Running scraper
    s.scrape_messages(chat_username)


if __name__ == "__main__":
    fire.Fire(scrape)
