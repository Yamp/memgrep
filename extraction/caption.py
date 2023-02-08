import warnings
from pathlib import Path

import torch
from PIL import Image
from lavis.models import load_model_and_preprocess


class ImageCaptioner:
    def __init__(self, model_name='blip_caption', model_type='base_coco'):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        if self.device == "cpu":
            warnings.warn('GPU is not available. CPU mode is activated (IT IS VERY SLOW)')
        self.model, self.vis_processors, _ = load_model_and_preprocess(
            name=model_name, model_type=model_type, is_eval=True, device=self.device)

    def caption(self, image: Path) -> str:
        raw_image = Image.open(image_path).convert("RGB")
        image = self.vis_processors["eval"](raw_image).unsqueeze(0).to(self.device)
        caption_str = self.model.generate({"image": image})
        return caption_str


if __name__ == '__main__':
    ic = ImageCaptioner()
    image_path = 'images/meme1.jpg'
    print(ic.caption(image_path))