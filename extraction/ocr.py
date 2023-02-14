import os
import string
import warnings
from pathlib import Path
from pprint import pprint

import easyocr
import enchant
from PIL import Image
from pytesseract import pytesseract


class OCRExtractor:
    def __init__(self, check_dict=False):
        self._check_dict = check_dict
        self.en_dict = enchant.Dict("en_US")
        self._easyocr = easyocr.Reader(["ru", "en"])
            
    def extract(self, image: Path) -> str:
        words = self._extract_easy_ocr(image).lower().split()
        words = [w for w in words if w.isalpha() and len(w) >= 2]
        if self._check_dict:
            words = [w for w in words if self.Pis_dict_word(w)]
        return str(u" ".join(words))

    def _is_dict_word(self, word: str) -> bool:
        return self._dict_en.check(word)

    def extract_dir(self, image_dir: Path) -> dict:
        if not os.path.isdir(image_dir):
            warnings.warn(f"Not a valid dir: {image_dir}")
            return {}
        result = {}
        for image_path in os.listdir(image_dir):
            if image_path.endswith(".jpg"):
                image_name = image_path[:-len(".jpg")]
                result[image_name] = self.extract(os.path.join(image_dir, image_path))
        return result

    def _extract_tesseract(
            self,
            image: Path,
            lang: str = "en",
    ) -> str:
        return pytesseract.image_to_string(Image.open(image), lang=lang)

    def _extract_easy_ocr(
            self,
            image: Path
    ) -> str:
        words = self._easyocr.readtext(Image.open(image), detail=0, paragraph=True)
        return u" ".join(words)


if __name__ == "__main__":
    ocr = OCRExtractor(check_dict=False)
    while True:
        image_path = input("Enter image(s) path: ")
        if not os.path.exists(image_path):
            pprint(f"Incorrect path {image_path}")
        elif os.path.isdir(image_path):
            pprint(ocr.extract_dir(image_path))
        else:
            pprint(ocr.extract(image_path))
