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

SAMPLES = []

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
