import os
import string
from pathlib import Path
from pprint import pprint
import warnings

from PIL import Image

import enchant
from pytesseract import pytesseract


class OCRExtractor:
    def __init__(self):
        self.dict_en = enchant.Dict("en_US")

    def extract(self, image: Path) -> str:
        words = ' '.join(self.extract_easy_ocr(image)).split()
        words = [w.translate(str.maketrans('', '', string.punctuation)) for w in words]
        words = [w for w in words if w.isalpha()]
        words = [w for w in words if self.dict_en.check(w)]
        return ' '.join(words).lower()

    def extract_dir(self, image_dir: Path) -> dict:
        if not os.path.isdir(image_dir):
            warnings.warn(f'Not a valid dir: {image_dir}')
            return {}
        result = {}
        for image_path in os.listdir(image_dir):
            if image_path.endswith('.jpg'):
                image_name = image_path[:-len('.jpg')]
                result[image_name] = self.extract(os.path.join(image_dir, image_path))
        return result

    def extract_tesseract(
            self,
            image: Path,
            lang: str = "rus",
    ) -> str:
        return pytesseract.image_to_string(Image.open(image), lang=lang)

    def extract_easy_ocr(
            self,
            image: Path,
            lang: str = "rus",
    ) -> list[str]:
        """Extract text from image using easyOCR."""
        try:
            import easyocr
        except ImportError:
            warnings.warn("easyOCR is not installed.")
            return ""

        reader = easyocr.Reader(["en"])
        words = reader.readtext(Image.open(image), detail=0)
        return words


if __name__ == '__main__':
    ocr = OCRExtractor()
    while True:
        image_path = input("Enter image(s) path: ")
        if not os.path.exists(image_path):
            pprint(f'Incorrect path {image_path}')
        elif os.path.isdir(image_path):
            pprint(ocr.extract_dir(image_path))
        else:
            pprint(ocr.extract(image_path))
