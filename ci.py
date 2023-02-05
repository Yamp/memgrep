import os
import sys

from PIL import Image
from clip_interrogator import Config, Interrogator


if __name__ == '__main__':

    ci = Interrogator(Config(clip_model_name="ViT-L-14/openai"))

    while True:
        image_path = input('Enter image path:\n')
        print(f'Loading image from {image_path}...')
        image = Image.open(image_path).convert('RGB')
        print(ci.interrogate(image))
        print()