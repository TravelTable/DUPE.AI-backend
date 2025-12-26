from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.database import init_db, SessionLocal, Product
import random

app = FastAPI(title="DUPE.AI Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def _startup():
    init_db()

@app.get("/_health")
def health():
    # Checks DB connectivity + pgvector
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        db.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        return {"ok": True}
    finally:
        db.close()

@app.post("/_seed_minimal")
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
            dict(name="Streetwear Leather Jacket", brand="Zara Dupe", price=89.99,
                 image_url="https://images.unsplash.com/photo-1551028919-38f4287c23f9",
                 buy_url="https://zara.com", embedding=rand_vec()),
            dict(name="Beige Trench Coat", brand="Burberry Original", price=2400.00,
                 image_url="https://images.unsplash.com/photo-1591047139829-d91aecb6caea",
                 buy_url="https://burberry.com", embedding=rand_vec()),
            dict(name="Casual Denim Jacket", brand="H&M", price=49.99,
                 image_url="https://images.unsplash.com/photo-1576871337622-98d48d1cf531",
                 buy_url="https://hm.com", embedding=rand_vec()),
        ]

        for it in items:
            db.add(Product(**it))
        db.commit()
        count = db.execute(text("SELECT COUNT(*) FROM products")).scalar()
        return {"seeded": 3, "total_products": int(count)}
    finally:
        db.close()

@app.get("/_tables")
def tables():
    db = SessionLocal()
    try:
        rows = db.execute(text("SELECT tablename FROM pg_tables WHERE schemaname='public';")).fetchall()
        return {"tables": [r[0] for r in rows]}
    finally:
        db.close()
