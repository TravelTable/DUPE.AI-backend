import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings
from loguru import logger

db_url = settings.DATABASE_URL
if not db_url:
    raise RuntimeError("DATABASE_URL not set. In Railway, set it to ${{ pgvector.DATABASE_URL }} on the backend service.")

# SQLAlchemy expects postgresql://
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

# Optional SSL control (Railway pgvector sometimes needs disable; you've seen this)
if settings.DB_SSLMODE and "sslmode=" not in db_url:
    sep = "&" if "?" in db_url else "?"
    db_url = f"{db_url}{sep}sslmode={settings.DB_SSLMODE}"

engine = create_engine(
    db_url,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=10,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def init_db() -> None:
    # Ensure pgvector
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        conn.commit()
    from app import models  # import to register models
    Base.metadata.create_all(bind=engine)
    with engine.connect() as conn:
        try:
            conn.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS products_embedding_idx "
                    "ON products USING ivfflat (embedding vector_l2_ops) "
                    "WITH (lists = 100);"
                )
            )
            conn.commit()
        except Exception:
            logger.exception("Failed to create pgvector index on products.embedding")
