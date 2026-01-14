from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models import Product

def top_matches(db: Session, vec: list, n: int = 5) -> List[Dict[str, Any]]:
    rows = (
        db.query(Product)
        .order_by(Product.embedding.l2_distance(vec))
        .limit(n)
        .all()
    )
    return [
        {
            "id": r.id,
            "name": r.name,
            "brand": r.brand,
            "category": r.category,
            "price": r.price,
            "currency": r.currency,
            "image_url": r.image_url,
            "buy_url": r.buy_url,
        }
        for r in rows
    ]
