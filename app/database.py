import os
from sqlalchemy import create_engine, Column, Integer, String, Float, text
from sqlalchemy.orm import sessionmaker, declarative_base
from pgvector.sqlalchemy import Vector

# Read connection string from env (works on Railway and locally).
# For local dev, you can set DATABASE_URL in a .env or your shell.
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

# Fallback for local testing (OPTIONAL: replace with your local string if you want)
# Example: "postgresql://dupe_admin:password123@localhost:5432/dupe_db"
if not DATABASE_URL:
    DATABASE_URL = "postgresql://dupe_admin:password123@localhost:5432/dupe_db"

# Railway sometimes provides 'postgres://'. SQLAlchemy requires 'postgresql://'.
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Some hosts require SSL. If your URL lacks sslmode, add it safely.
# (No-op if it’s already there.)
if "sslmode=" not in DATABASE_URL and "localhost" not in DATABASE_URL:
    sep = "&" if "?" in DATABASE_URL else "?"
    DATABASE_URL = f"{DATABASE_URL}{sep}sslmode=require"

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,         # avoid stale connections
    pool_size=5,
    max_overflow=5,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ------------ Models ------------
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    brand = Column(String)
    price = Column(Float)
    image_url = Column(String)
    buy_url = Column(String)

    # 512 dims is standard for CLIP
    embedding = Column(Vector(512))


# ------------ Init / Migrate ------------
def init_db() -> None:
    # Ensure the 'vector' extension exists (safe to run repeatedly).
    with engine.connect() as conn:
        try:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        except Exception:
            # On managed instances without SUPERUSER rights, you may have enabled it via the UI already.
            pass
        conn.commit()

    # Create tables
    Base.metadata.create_all(bind=engine)
