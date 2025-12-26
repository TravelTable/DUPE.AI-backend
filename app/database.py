import os
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker, declarative_base
from pgvector.sqlalchemy import Vector

# 1. READ FROM ENVIRONMENT VARIABLE (Or paste your Railway URL here for testing)
# REPLACE THE STRING BELOW WITH YOUR COPIED RAILWAY URL
DATABASE_URL = "postgresql://postgres:password@roundhouse.proxy.rlwy.net:PORT/railway"

# Railway uses "postgres://" but SQLAlchemy needs "postgresql://"
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    brand = Column(String)
    price = Column(Float)
    image_url = Column(String)
    buy_url = Column(String)
    embedding = Column(Vector(512)) 

def init_db():
    # We already enabled the extension in the Railway UI, 
    # but this line is safe to keep just in case.
    with engine.connect() as conn:
        conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
        conn.commit()
    Base.metadata.create_all(bind=engine)