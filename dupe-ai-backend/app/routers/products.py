from fastapi import APIRouter, Query
from sqlalchemy import and_
from app.database import SessionLocal
from app.models import Product
from app.schemas import ProductOut

router = APIRouter(prefix="/products", tags=["products"])

@router.get("", response_model=list[ProductOut])
def list_products(
    q: str | None = Query(default=None),
    brand: str | None = Query(default=None),
    category: str | None = Query(default=None),
    min_price: float | None = Query(default=None),
    max_price: float | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    db = SessionLocal()
    try:
        stmt = db.query(Product)
        filters = []
        if q:
            like = f"%{q}%"
            stmt = stmt.filter((Product.name.ilike(like)) | (Product.brand.ilike(like)))
        if brand:
            filters.append(Product.brand.ilike(f"%{brand}%"))
        if category:
            filters.append(Product.category.ilike(f"%{category}%"))
        if min_price is not None:
            filters.append(Product.price >= min_price)
        if max_price is not None:
            filters.append(Product.price <= max_price)
        if filters:
            stmt = stmt.filter(and_(*filters))
        rows = stmt.order_by(Product.updated_at.desc()).limit(limit).offset(offset).all()
        return [
            ProductOut(
                id=r.id, name=r.name, brand=r.brand, category=r.category,
                price=r.price, currency=r.currency, image_url=r.image_url, buy_url=r.buy_url
            )
            for r in rows
        ]
    finally:
        db.close()

@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int):
    db = SessionLocal()
    try:
        r = db.query(Product).get(product_id)
        if not r:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Not found")
        return ProductOut(
            id=r.id, name=r.name, brand=r.brand, category=r.category,
            price=r.price, currency=r.currency, image_url=r.image_url, buy_url=r.buy_url
        )
    finally:
        db.close()
