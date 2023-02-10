#!/usr/bin/env python3

from pathlib import Path

from loguru import logger

from data.data_storage import DataStorage
from data.pg.postgre_db import PostgresDB
from data.redis_db import RedisDB
from data.s3_db import S3DB
from extraction.caption import ImageCaptioner


def recognise_image(id: str, data: bytes) -> str:
    path = Path(f"{id}.jpg")
    path.write_bytes(data)
    return ImageCaptioner().caption(path)


def main():
    logger.info("Initializing s3...")
    s3 = S3DB()
    logger.info("Initializing redis...")
    redis = RedisDB()
    logger.info("Initializing postgres...")
    pg = PostgresDB()

    logger.info("Creating storage...")
    storage = DataStorage(s3, redis, pg)
    res = storage.get_all_images()

    for id, img in res.items():
        logger.info(f"Recognising image {id}...")
        caption = recognise_image(str(id), img.data)
        logger.info(f"Caption: {caption}")
        # storage.set_image_caption(id, caption)

if __name__ == "__main__":
    main()
