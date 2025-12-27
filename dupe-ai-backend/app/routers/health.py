import random

from fastapi import APIRouter
from sqlalchemy import text
from app.database import SessionLocal, engine
from app.models import Product

router = APIRouter(tags=["system"])

@router.get("/_health")
def health():
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
    return {"ok": True}

@router.get("/_tables")
def tables():
    with engine.connect() as conn:
        rows = conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname='public'")).fetchall()
    return {"tables": [r[0] for r in rows]}

@router.post("/_seed_minimal")
def seed_minimal():
    """
    Cloud-only sanity seed: inserts 3 products with random 512-d vectors.
    This verifies pgvector + schema without heavy model downloads yet.
    """
    db = SessionLocal()
    try:
        def rand_vec():
            return [random.random() for _ in range(512)]

        items = [
            dict(source="seed", name="Streetwear Leather Jacket", brand="Zara Dupe", price=89.99,
                 image_url="https://images.unsplash.com/photo-1551028919-38f4287c23f9",
                 buy_url="https://zara.com", embedding=rand_vec()),
            dict(source="seed", name="Beige Trench Coat", brand="Burberry Original", price=2400.00,
                 image_url="https://images.unsplash.com/photo-1591047139829-d91aecb6caea",
                 buy_url="https://burberry.com", embedding=rand_vec()),
            dict(source="seed", name="Casual Denim Jacket", brand="H&M", price=49.99,
                 image_url="https://images.unsplash.com/photo-1576871337622-98d48d1cf531",
                 buy_url="https://hm.com", embedding=rand_vec()),
        ]

        for it in items:
            db.add(Product(**it))
        db.commit()
        return {"seeded": 3, "total_products": db.query(Product).count()}
    finally:
        db.close()
