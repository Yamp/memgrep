#!/usr/bin/env python3
import sys

sys.path.extend([".", "..", "../.."])

from pathlib import Path

from loguru import logger

from data.data_storage import get_default_storage
from extraction.caption import ImageCaptioner
from extraction.ocr import OCRExtractor

def save_image(id: str, data: bytes) -> Path:
    path = Path(f"{id}.jpg")
    path.write_bytes(data)
    return path

def main():
    storage = get_default_storage()
    res = storage.get_all_images(limit=1000)

    ic = ImageCaptioner()
    ocr = OCRExtractor()

    for id, img in res.items():
        logger.info(f"Recognising image {id}...")
        item = save_image(id, img.data)
        caption = ic.caption(item)
        text = ocr.extract(item)
        item.unlink()

        logger.info(f"Caption: {caption}")
        logger.info(f"OCR: {text}")
        pg.add_recognition(int(id), caption, text)

        # storage.set_image_caption(id, caption)


if __name__ == "__main__":
    main()
