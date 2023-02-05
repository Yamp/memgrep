from pathlib import Path

from PIL import Image

import pytesseract

# https://www.google.com/search?q=easy_tesseract&newwindow=1&sxsrf=AJOqlzWqC3xhLtgG1mMbi3f2UaINveYIxQ%3A1675606506042&ei=6rnfY6mdAtvJz7sP3M6g0AQ&ved=0ahUKEwipus3UyP78AhXb5HMBHVwnCEoQ4dUDCA8&uact=5&oq=easy_tesseract&gs_lcp=Cgxnd3Mtd2l6LXNlcnAQAzIGCAAQHhAPMgYIABAIEB4yCAgAEAgQHhAKMgUIABCGAzIFCAAQhgM6CggAEEcQ1gQQsAM6BAgjECc6BQgAEJECOgUIABCABDoHCCMQ6gIQJzoLCC4QgwEQsQMQgAQ6CwgAEIAEELEDEIMBOggIABCABBCxAzoLCC4QsQMQgwEQ1AI6BAgAEEM6CggAELEDEIMBEEM6EAgAEIAEEBQQhwIQsQMQgwE6EQguEIAEELEDEIMBEMcBENEDOhAILhCxAxCDARDHARDRAxBDOgsILhCABBCxAxDUAjoKCAAQgAQQFBCHAjoHCAAQgAQQCjoNCC4QgAQQxwEQ0QMQCjoECAAQHjoICAAQCBAeEA9KBAhBGABKBAhGGABQ_tpXWMiTWGDolFhoA3ABeACAAb0CiAHRFJIBCDAuMTQuMS4xmAEAoAEBsAEKyAEIwAEB&sclient=gws-wiz-serp

folder = Path(__file__).parent / 'images'
# iterate over all files in the folder
for file in folder.iterdir():
    # check if the file is a png file
    if file.suffix == '.jpg':
        # open the image
        print(file.name)
        try:
            image = Image.open(file)
            # convert the image to a string
            text1 = pytesseract.image_to_string(image, lang='rus')
            text2 = pytesseract.image_to_string(image, lang='eng')
            # print the text
            print(text1)
            print(text2)
            print('-' * 80)
        except:
            pass

