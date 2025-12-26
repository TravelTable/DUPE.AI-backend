from fastapi import APIRouter
from sqlalchemy import text
from app.database import engine

router = APIRouter(tags=["system"])

@router.get("/_health")
def health():
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
    return {"ok": True}

@router.get("/_tables")
def tables():
    with engine.connect() as conn:
        rows = conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname='public'")).fetchall()
    return {"tables": [r[0] for r in rows]}
