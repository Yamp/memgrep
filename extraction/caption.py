import os
from pathlib import Path
from pprint import pprint
import warnings

import torch
from lavis.models import load_model_and_preprocess
from PIL import Image


class ImageCaptioner:
    def __init__(self, model_name="blip_caption", model_type="base_coco"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        if self.device == "cpu":
            warnings.warn("GPU is not available. CPU mode is activated (IT IS VERY SLOW)")
        self.model, self.vis_processors, _ = load_model_and_preprocess(
            name=model_name, model_type=model_type, is_eval=True, device=self.device)

    def caption(self, image_path: Path) -> str:
        if not os.path.exists(image_path):
            warnings.warn(f'{image_path} does not exist')
            return ''
        raw_image = Image.open(image_path).convert("RGB")
        image = self.vis_processors["eval"](raw_image).unsqueeze(0).to(self.device)
        caption_str = self.model.generate({"image": image})
        return caption_str

    def caption_dir(self, image_dir: Path) -> dict:
        if not os.path.isdir(image_dir):
            warnings.warn(f'{image_dir} is not valid dir')
            return {}
        result = {}
        for image_path in os.listdir(image_dir):
            if image_path.endswith('.jpg'):
                image_name = image_path[:-len('.jpg')]
                result[image_name] = self.caption(os.path.join(image_dir, image_path))
        return result


if __name__ == "__main__":
    ic = ImageCaptioner()
    while True:
        image_path = input("Enter image(s) path: ")
        if not os.path.exists(image_path):
            pprint(f'Incorrect path {image_path}')
        elif os.path.isdir(image_path):
            pprint(ic.caption_dir(image_path))
        else:
            pprint(ic.caption(image_path))
