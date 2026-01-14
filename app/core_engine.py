import torch
from loguru import logger
from PIL import Image
from ultralytics import YOLO
from transformers import CLIPProcessor, CLIPModel

class DupeEngine:
    def __init__(self):
        logger.info("Loading DUPE.AI models (first run takes time).")
        
        # 1. The Cutter: YOLOv8 (Small version for speed)
        # It will auto-download 'yolov8n-seg.pt'
        self.detector = YOLO('yolov8n-seg.pt') 

        # 2. The Matcher: Fashion-CLIP
        model_id = "patrickjohncyh/fashion-clip"
        self.processor = CLIPProcessor.from_pretrained(model_id)
        self.model = CLIPModel.from_pretrained(model_id)
        
        logger.info("DUPE.AI models loaded.")

    def cut_clothes(self, image_path):
        """Detects items, crops them, returns list of images."""
        results = self.detector(image_path)
        crops = []
        
        # We only care about these detected classes
        fashion_classes = ['person', 'backpack', 'handbag', 'tie', 'suitcase']
        
        for result in results:
            boxes = result.boxes.xyxy.cpu().numpy()
            classes = result.boxes.cls.cpu().numpy()
            names = result.names
            
            original_img = Image.open(image_path)
            
            for box, cls in zip(boxes, classes):
                label = names[int(cls)]
                if label in fashion_classes:
                    x1, y1, x2, y2 = box
                    cropped = original_img.crop((x1, y1, x2, y2))
                    crops.append({"label": label, "image": cropped})
                    
        return crops

    def get_vector(self, image):
        """Turns an image into 512 numbers."""
        inputs = self.processor(images=image, return_tensors="pt")
        with torch.no_grad():
            features = self.model.get_image_features(**inputs)
        
        # Normalize
        features = features / features.norm(p=2, dim=-1, keepdim=True)
        return features.numpy()[0].tolist()
