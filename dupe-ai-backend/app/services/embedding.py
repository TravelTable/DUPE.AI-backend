from functools import lru_cache
from io import BytesIO

import requests
import torch
from loguru import logger
from PIL import Image, UnidentifiedImageError
from transformers import CLIPProcessor, CLIPModel

@lru_cache(maxsize=1)
def _load():
    model_id = "patrickjohncyh/fashion-clip"
    logger.info("Loading Fashion-CLIP model: {}", model_id)
    processor = CLIPProcessor.from_pretrained(model_id)
    model = CLIPModel.from_pretrained(model_id)
    model.eval()
    return processor, model

def image_bytes_to_vec(b: bytes):
    processor, model = _load()
    try:
        img = Image.open(BytesIO(b)).convert("RGB")
    except UnidentifiedImageError as exc:
        raise ValueError("invalid image data") from exc
    inputs = processor(images=img, return_tensors="pt")
    with torch.no_grad():
        feats = model.get_image_features(**inputs)
    feats = feats / feats.norm(p=2, dim=-1, keepdim=True)
    return feats.cpu().numpy()[0].tolist()

def image_url_to_vec(url: str, timeout: int = 30):
    try:
        r = requests.get(url, timeout=timeout)
        r.raise_for_status()
    except requests.RequestException as exc:
        raise ValueError("unable to fetch image url") from exc
    return image_bytes_to_vec(r.content)
