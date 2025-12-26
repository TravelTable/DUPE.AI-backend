from pydantic import BaseModel, HttpUrl
from typing import Optional, List

class ProductOut(BaseModel):
    id: int
    name: str
    brand: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    currency: Optional[str] = None
    image_url: str
    buy_url: str

class SearchResponse(BaseModel):
    matches: List[ProductOut]

class ProductsQuery(BaseModel):
    q: Optional[str] = None
    brand: Optional[str] = None
    category: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    limit: int = 20
    offset: int = 0
