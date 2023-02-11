#!/usr/bin/env python3
import sys

sys.path.extend([".", "..", "../.."])

from pathlib import Path

from loguru import logger

from data.data_storage import DataStorage
from data.pg.postgre_db import PostgresDB
from data.s3_db import S3DB
from extraction.caption import ImageCaptioner
from extraction.ocr import OCRExtractor

def save_image(id: str, data: bytes) -> Path:
    path = Path(f"{id}.jpg")
    path.write_bytes(data)
    return path

def main():
    logger.info("Initializing s3...")
    s3 = S3DB()
    # logger.info("Initializing redis...")
    # redis = RedisDB()
    logger.info("Initializing postgres...")
    pg = PostgresDB()

    logger.info("Creating storage...")
    storage = DataStorage(s3, None, pg)
    res = storage.get_all_images(limit=1000)

    ic = ImageCaptioner()
    ocr = OCRExtractor()


    for id, img in res.items():
        logger.info(f"Recognising image {id}...")
        item = save_image(id, img.data)
        caption = ic.get_caption(item)
        text = ocr.extract(item)
        item.unlink()

        logger.info(f"Caption: {caption}")
        pg.add_recognition(int(id), caption, text)

        # storage.set_image_caption(id, caption)


if __name__ == "__main__":
    main()
