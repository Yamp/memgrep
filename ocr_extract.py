from pathlib import Path

from PIL import Image

import pytesseract

folder = Path(__file__).parent / 'images'
# iterate over all files in the folder
for file in folder.iterdir():
    # check if the file is a png file
    if file.suffix == '.jpg':
        # open the image
        image = Image.open(file)
        # convert the image to a string
        text = pytesseract.image_to_string(image, lang='ru')
        # print the text
        print(text)

print(pytesseract.image_to_string('test.png'))
