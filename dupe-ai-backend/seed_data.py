import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import Product
from app.services.embedding import image_url_to_vec

def _build_engine():
    db_url = os.getenv("DATABASE_URL", "").strip()
    if not db_url:
        raise RuntimeError("Set DATABASE_URL to your Railway pgvector URL")
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    sslmode = os.getenv("DB_SSLMODE", "").strip().lower()
    if sslmode and "sslmode=" not in db_url:
        sep = "&" if "?" in db_url else "?"
        db_url = f"{db_url}{sep}sslmode={sslmode}"
    return create_engine(db_url, pool_pre_ping=True)

SAMPLES = [
    # Dream/Steal pairs
    dict(name="Rick Owens Bauhaus Leather Jacket", brand="Rick Owens (Dream)", category="jacket",
         price=4200.00, currency="USD",
         image_url="https://images.unsplash.com/photo-1551028919-38f4287c23f9?auto=format&fit=crop&w=800&q=80",
         buy_url="https://rickowens.eu"),
    dict(name="Faux Leather Biker Jacket", brand="Zara (Steal)", category="jacket",
         price=89.90, currency="USD",
         image_url="https://images.unsplash.com/photo-1520975661595-dc998ddbe94f?auto=format&fit=crop&w=800&q=80",
         buy_url="https://zara.com"),
    dict(name="Hermès Birkin 30", brand="Hermès (Dream)", category="bag",
         price=12000.00, currency="USD",
         image_url="https://images.unsplash.com/photo-1584917865442-de89df76afd3?auto=format&fit=crop&w=800&q=80",
         buy_url="https://hermes.com"),
    dict(name="Top Handle Structured Bag", brand="H&M (Steal)", category="bag",
         price=39.99, currency="USD",
         image_url="https://images.unsplash.com/photo-1591561954557-26941169b49e?auto=format&fit=crop&w=800&q=80",
         buy_url="https://hm.com"),
    dict(name="Balenciaga Triple S", brand="Balenciaga (Dream)", category="sneaker",
         price=1150.00, currency="USD",
         image_url="https://images.unsplash.com/photo-1515955656352-a1fa3ffcd111?auto=format&fit=crop&w=800&q=80",
         buy_url="https://balenciaga.com"),
    dict(name="Chunky Sole Dad Sneaker", brand="ASOS Design (Steal)", category="sneaker",
         price=45.00, currency="USD",
         image_url="https://images.unsplash.com/photo-1552346154-21d32810aba3?auto=format&fit=crop&w=800&q=80",
         buy_url="https://asos.com"),
]

def main():
    engine = _build_engine()
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    try:
        inserted = 0
        for item in SAMPLES:
            vec = image_url_to_vec(item["image_url"])
            p = Product(**item, embedding=vec)
            db.add(p)
            inserted += 1
        db.commit()
        total = db.execute("SELECT COUNT(*) FROM products").scalar()
        print(f"✅ Seed complete. Inserted {inserted}. Total {total}.")
    finally:
        db.close()

if __name__ == "__main__":
    sys.exit(main())
