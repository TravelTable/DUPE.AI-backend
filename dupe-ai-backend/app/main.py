from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.logging_conf import setup_logging
from app.config import settings
from app.database import init_db
from app.services import embedding
from app.routers import health, search, products, iap

setup_logging(settings.LOG_LEVEL)

app = FastAPI(title="DUPE.AI Backend", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.CORS_ALLOW_ORIGINS.split(",") if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def _startup():
    init_db()
    try:
        embedding._load()
    except Exception:
        from loguru import logger
        logger.exception("Failed to preload Fashion-CLIP model")

app.include_router(health.router)
app.include_router(search.router)
app.include_router(products.router)
app.include_router(iap.router)
