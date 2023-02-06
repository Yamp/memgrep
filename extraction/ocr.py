from pathlib import Path

import easyocr
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
        reader = easyocr.Reader(["ru", "en"])
        return reader.readtext(Image.open(image))
