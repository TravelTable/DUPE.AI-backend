from fastapi import APIRouter, UploadFile, File, Body, Request, HTTPException
from loguru import logger
from app.database import SessionLocal
from app.services.embedding import image_bytes_to_vec, image_url_to_vec
from app.services.search import top_matches
from app.services.rate_limit import token_bucket
from app.schemas import SearchResponse
from app.services.cloudinary import upload_image
from app.services.serp import search_by_image
from app.services.openai_service import analyze_product_similarity, get_fashion_advice

router = APIRouter(prefix="/search", tags=["search"])

def _ip(req: Request) -> str:
    return req.headers.get("x-forwarded-for", req.client.host or "unknown").split(",")[0].strip()

@router.post("/url", response_model=SearchResponse)
def search_url(req: Request, image_url: str = Body(..., embed=True)):
    if not token_bucket(f"rl:url:{_ip(req)}", limit=20, window_sec=60):
        raise HTTPException(status_code=429, detail="rate limit")
    db = SessionLocal()
    try:
        try:
            vec = image_url_to_vec(image_url)
        except ValueError as exc:
            logger.warning("search/url invalid image: {}", exc)
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except Exception as exc:
            logger.exception("search/url embedding failure")
            raise HTTPException(status_code=500, detail="embedding failed") from exc
        matches = top_matches(db, vec, n=5)
        return {"matches": matches}
    finally:
        db.close()

@router.post("/file", response_model=SearchResponse)
async def search_file(req: Request, file: UploadFile = File(...)):
    if not token_bucket(f"rl:file:{_ip(req)}", limit=10, window_sec=60):
        raise HTTPException(status_code=429, detail="rate limit")
    
    b = await file.read()
    db = SessionLocal()
    
    try:
        # 1. Local Vector Search (pgvector)
        try:
            vec = image_bytes_to_vec(b)
            local_matches = top_matches(db, vec, n=5)
        except Exception as exc:
            logger.exception("Local search failed")
            local_matches = []

        # 2. Web/Replica Search (SerpApi + Cloudinary)
        web_matches = []
        try:
            # Upload to Cloudinary to get a URL for SerpApi
            image_url = upload_image(b)
            # Search web for replicas
            web_matches = await search_by_image(image_url)
        except Exception as exc:
            logger.exception("Web search failed")

        # 3. AI Analysis (OpenAI)
        all_matches = local_matches + web_matches
        try:
            if web_matches and 'image_url' in locals():
                all_matches = await analyze_product_similarity(image_url, all_matches)
        except Exception as exc:
            logger.exception("AI analysis failed")

        return {"matches": all_matches}
    finally:
        db.close()
