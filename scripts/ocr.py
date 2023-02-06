#!/usr/bin/env python3

from pathlib import Path

import fire
from loguru import logger

from extraction.ocr import OCRExtractor


def test(
        path: Path,
):
    extractor = OCRExtractor()

    for file in path.iterdir():
        logger.info(file.name)
        if file.suffix == ".jpg":
            logger.info(extractor.extract(file))
        else:
            logger.warning("Not a jpg file, skipping")


if __name__ == "__main__":
    fire.Fire(test)
