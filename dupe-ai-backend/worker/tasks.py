from worker.celery_app import celery
from app.database import SessionLocal
from app.models import Product
from app.services.embedding import image_url_to_vec
from loguru import logger

@celery.task(name="embed_product")
def embed_product(product_id: int, image_url: str):
    db = SessionLocal()
    try:
        vec = image_url_to_vec(image_url)
        row = db.query(Product).get(product_id)
        if not row:
            logger.warning(f"Product {product_id} disappeared")
            return
        row.embedding = vec
        db.commit()
        logger.info(f"Embedded product {product_id}")
    except Exception as e:
        logger.exception(f"embed_product failed: {e}")
        raise
    finally:
        db.close()
