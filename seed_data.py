import os
import sys
import torch
from PIL import Image
import requests
from io import BytesIO
from transformers import CLIPProcessor, CLIPModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Product, Base  # your models


def build_engine_from_env():
    db_url = os.getenv("DATABASE_URL", "").strip()
    if not db_url:
        raise RuntimeError("Set DATABASE_URL in your shell to the Railway pgvector URL")

    # SQLAlchemy wants postgresql://
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    sslmode = os.getenv("DB_SSLMODE", "").strip().lower()
    if sslmode and "sslmode=" not in db_url:
        sep = "&" if "?" in db_url else "?"
        db_url = f"{db_url}{sep}sslmode={sslmode}"

    print(f"🚀 Connecting to: {db_url}")
    return create_engine(db_url, pool_pre_ping=True)


print("🧠 Loading Fashion-CLIP...")
model_id = "patrickjohncyh/fashion-clip"
processor = CLIPProcessor.from_pretrained(model_id)
model = CLIPModel.from_pretrained(model_id)
model.eval()


def embed_from_url(url: str):
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        img = Image.open(BytesIO(r.content)).convert("RGB")
        inputs = processor(images=img, return_tensors="pt")
        with torch.no_grad():
            feats = model.get_image_features(**inputs)
        feats = feats / feats.norm(p=2, dim=-1, keepdim=True)
        return feats.cpu().numpy()[0].tolist()
    except Exception as e:
        print(f"❌ Failed {url}: {e}")
        return None


# Dream vs Steal seed pairs for your “Reality Slider”
SEED_ITEMS = [
    # Leather Jacket
    {
        "name": "Rick Owens Bauhaus Leather Jacket",
        "brand": "Rick Owens (The Dream)",
        "price": 4200.00,
        "image_url": "https://images.unsplash.com/photo-1551028919-38f4287c23f9?auto=format&fit=crop&w=800&q=80",
        "buy_url": "https://rickowens.eu",
    },
    {
        "name": "Faux Leather Biker Jacket",
        "brand": "Zara (The Steal)",
        "price": 89.90,
        "image_url": "https://images.unsplash.com/photo-1520975661595-dc998ddbe94f?auto=format&fit=crop&w=800&q=80",
        "buy_url": "https://zara.com",
    },
    # Designer Bag
    {
        "name": "Hermès Birkin 30",
        "brand": "Hermès (The Dream)",
        "price": 12000.00,
        "image_url": "https://images.unsplash.com/photo-1584917865442-de89df76afd3?auto=format&fit=crop&w=800&q=80",
        "buy_url": "https://hermes.com",
    },
    {
        "name": "Top Handle Structured Bag",
        "brand": "H&M (The Steal)",
        "price": 39.99,
        "image_url": "https://images.unsplash.com/photo-1591561954557-26941169b49e?auto=format&fit=crop&w=800&q=80",
        "buy_url": "https://hm.com",
    },
    # Sneakers
    {
        "name": "Balenciaga Triple S",
        "brand": "Balenciaga (The Dream)",
        "price": 1150.00,
        "image_url": "https://images.unsplash.com/photo-1515955656352-a1fa3ffcd111?auto=format&fit=crop&w=800&q=80",
        "buy_url": "https://balenciaga.com",
    },
    {
        "name": "Chunky Sole Dad Sneaker",
        "brand": "ASOS Design (The Steal)",
        "price": 45.00,
        "image_url": "https://images.unsplash.com/photo-1552346154-21d32810aba3?auto=format&fit=crop&w=800&q=80",
        "buy_url": "https://asos.com",
    },
]


def main():
    engine = build_engine_from_env()
    Session = sessionmaker(bind=engine)
    db = Session()

    # Ensure tables exist (pgvector extension should already be enabled by backend)
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"⚠️ Table creation warning: {e}")

    print("🌱 Seeding...")
    added = 0
    for item in SEED_ITEMS:
        print(f"→ {item['name']}")
        vec = embed_from_url(item["image_url"])
        if not vec:
            continue
        db.add(Product(
            name=item["name"],
            brand=item["brand"],
            price=item["price"],
            image_url=item["image_url"],
            buy_url=item["buy_url"],
            embedding=vec,
        ))
        added += 1

    db.commit()
    total = db.execute("SELECT COUNT(*) FROM products").scalar()
    db.close()
    print(f"✅ Done. Inserted {added}. Total rows: {total}")


if __name__ == "__main__":
    sys.exit(main())
