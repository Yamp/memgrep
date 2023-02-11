import os
from pathlib import Path
from pprint import pprint
import warnings

from PIL import Image
from pytesseract import pytesseract


class OCRExtractor:
    def __init__(self):
        pass
        # self.image = image

    def extract(self, image: Path) -> str:
        s = "|".join([
            self.extract_tesseract(image, lang="rus"),
            self.extract_tesseract(image, lang="eng"),
            str(self.extract_easy_ocr(image)),
        ])
        s = " ".join(s.split())
        s = "".join([c for c in s if c.isalpha() or c.isdigit() or c == " "])
        s = s.lower()
        return s

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
    ) -> str:
        """Extract text from image using easyOCR."""
        try:
            import easyocr
        except ImportError:
            warnings.warn("easyOCR is not installed.")
            return ""

        reader = easyocr.Reader(["ru", "en"])
        return reader.readtext(Image.open(image))


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
