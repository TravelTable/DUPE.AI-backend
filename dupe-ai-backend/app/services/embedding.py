import torch
from transformers import CLIPProcessor, CLIPModel
from PIL import Image
from io import BytesIO
import requests
from functools import lru_cache

@lru_cache(maxsize=1)
def _load():
    model_id = "patrickjohncyh/fashion-clip"
    processor = CLIPProcessor.from_pretrained(model_id)
    model = CLIPModel.from_pretrained(model_id)
    model.eval()
    return processor, model

def image_bytes_to_vec(b: bytes):
    processor, model = _load()
    img = Image.open(BytesIO(b)).convert("RGB")
    inputs = processor(images=img, return_tensors="pt")
    with torch.no_grad():
        feats = model.get_image_features(**inputs)
    feats = feats / feats.norm(p=2, dim=-1, keepdim=True)
    return feats.cpu().numpy()[0].tolist()

def image_url_to_vec(url: str, timeout: int = 30):
    r = requests.get(url, timeout=timeout)
    r.raise_for_status()
    return image_bytes_to_vec(r.content)
