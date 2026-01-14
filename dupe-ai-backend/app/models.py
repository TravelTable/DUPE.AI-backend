from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
from pgvector.sqlalchemy import Vector

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    source = Column(String, nullable=True)              # "asos", "shein", "vinted" etc.
    external_id = Column(String, nullable=True)         # source item id
    name = Column(String, index=True, nullable=False)
    brand = Column(String, index=True, nullable=True)
    category = Column(String, index=True, nullable=True)
    price = Column(Float, nullable=True)
    currency = Column(String, default="USD")
    image_url = Column(String, nullable=False)
    buy_url = Column(String, nullable=False)
    attrs = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    embedding = Column(Vector(512))  # CLIP vector

    __table_args__ = (
        UniqueConstraint('source', 'external_id', name='uix_source_external'),
    )

class Upload(Base):
    __tablename__ = "uploads"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=True)  # optional until auth lands
    url = Column(String, nullable=True)
    sha256 = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Detection(Base):
    __tablename__ = "detections"
    id = Column(Integer, primary_key=True)
    upload_id = Column(Integer, ForeignKey("uploads.id"), nullable=False)
    label = Column(String, nullable=True)
    bbox = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    upload = relationship("Upload")

class Match(Base):
    __tablename__ = "matches"
    id = Column(Integer, primary_key=True)
    detection_id = Column(Integer, ForeignKey("detections.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    score = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    detection = relationship("Detection")
    product = relationship("Product")
