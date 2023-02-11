import os
import warnings
from pathlib import Path

import torch
from PIL import Image


class ImageCaptioner:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        if self.device == "cpu":
            warnings.warn("GPU is not available. CPU mode is activated (IT IS VERY SLOW)")
        self.has_lavis = self._init_lavis()
        self.has_ci = self._init_ci()
        if not self.has_lavis and not self.has_ci:
            warnings.warn("Neither lavis nor clip-interrogator is not configured, empty results will be provided")

    def caption(self, image_path: Path) -> str:
        if not os.path.exists(image_path):
            warnings.warn(f"{image_path} does not exist")
            return ""
        raw_image = Image.open(image_path).convert("RGB")
        if self.has_ci:
            return self._caption_ci(raw_image)
        else:
            return self._caption_lavis(raw_image)

    def caption_dir(self, image_dir: Path) -> dict:
        if not os.path.isdir(image_dir):
            warnings.warn(f"{image_dir} is not valid dir")
            return {}
        result = {}
        for image_path in os.listdir(image_dir):
            if image_path.endswith(".jpg"):
                image_name = image_path[:-len(".jpg")]
                result[image_name] = self.caption(os.path.join(image_dir, image_path))
        return result

    def _init_lavis(self, model_name="blip_caption", model_type="base_coco") -> bool:
        try:
            from lavis.models import load_model_and_preprocess
        except ImportError:
            warnings.warn("Lavis is not installed.")
            return False
        self.lavis, self.vis_processors, _ = load_model_and_preprocess(name=self.model_name,
            model_type=model_type, is_eval=True, device=self.device)
        return True

    def _init_ci(self, model_name="ViT-L-14/openai", chunk_size=512):
        try:
            import clip_interrogator as ci
        except ImportError:
            warnings.warn("clip_interrogator is not installed.")
            return False
        self.config = ci.Config(device=self.device, clip_model_name=model_name, chunk_size=chunk_size)
        self.ci = ci.Interrogator(self.config)
        return True

    def _caption_lavis(self, image: Image) -> str:
        image = self.vis_processors["eval"](image).unsqueeze(0).to(self.device)
        caption_str = self.model.generate({"image": image})
        return caption_str

    def _caption_ci(self, image: Image, mode="caption") -> str:
        if mode == "best":
            return self.ci.interrogate(image)
        elif mode == "classic":
            return self.ci.interrogate_classic(image)
        elif mode == "fast":
            return self.ci.interrogate_fast(image)
        elif mode == "caption":
            return self.ci.generate_caption(image)
        else:
            warnings.warn(f"Unsupported mode {mode}")
            return ""

if __name__ == "__main__":
    ic = ImageCaptioner()
    while True:
        image_path = input("Enter image(s) path: ")
        if not os.path.exists(image_path):
            pass
        elif os.path.isdir(image_path):
            pass
        else:
            pass
