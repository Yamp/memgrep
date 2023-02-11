#!/usr/bin/env python3
import sys

sys.path.extend([".", "..", "../.."])

from pathlib import Path

from loguru import logger

from data.data_storage import DataStorage
from data.pg.postgre_db import PostgresDB
from data.s3_db import S3DB
from extraction.caption import ImageCaptioner


def recognise_image(id: str, data: bytes, ic: ImageCaptioner) -> str:
    path = Path(f"{id}.jpg")
    path.write_bytes(data)
    res = ic.caption(path)
    path.unlink()
    return res


def main():
    logger.info("Initializing s3...")
    s3 = S3DB()
    # logger.info("Initializing redis...")
    # redis = RedisDB()
    logger.info("Initializing postgres...")
    pg = PostgresDB()

    logger.info("Creating storage...")
    storage = DataStorage(s3, None, pg)
    res = storage.get_all_images()

    ic = ImageCaptioner()
    for id, img in res.items():
        logger.info(f"Recognising image {id}...")
        caption = recognise_image(str(id), img.data, ic)
        logger.info(f"Caption: {caption}")
        pg.add_recognition(int(id), caption)

        # storage.set_image_caption(id, caption)


if __name__ == "__main__":
    main()
