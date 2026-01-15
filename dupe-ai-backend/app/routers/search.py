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
async def search_url(req: Request, image_url: str = Body(..., embed=True)):
    if not token_bucket(f"rl:url:{_ip(req)}", limit=20, window_sec=60):
        raise HTTPException(status_code=429, detail="rate limit")
    
    try:
        # Search web for replicas directly
        web_matches = await search_by_image(image_url)
        
        # AI Analysis (OpenAI)
        try:
            web_matches = await analyze_product_similarity(image_url, web_matches)
        except Exception as exc:
            logger.exception("AI analysis failed")
            
        return {"matches": web_matches}
    except Exception as exc:
        logger.exception("search/url failure")
        raise HTTPException(status_code=500, detail="search failed") from exc

@router.post("/file", response_model=SearchResponse)
async def search_file(req: Request, file: UploadFile = File(...)):
    if not token_bucket(f"rl:file:{_ip(req)}", limit=10, window_sec=60):
        raise HTTPException(status_code=429, detail="rate limit")
    
    b = await file.read()
    
    try:
        # 1. Web/Replica Search (SerpApi + Cloudinary)
        web_matches = []
        try:
            # Upload to Cloudinary to get a URL for SerpApi
            image_url = upload_image(b)
            # Search web for replicas
            web_matches = await search_by_image(image_url)
        except Exception as exc:
            logger.exception("Web search failed")
            raise HTTPException(status_code=500, detail="web search failed") from exc

        # 2. AI Analysis (OpenAI)
        try:
            if web_matches:
                web_matches = await analyze_product_similarity(image_url, web_matches)
        except Exception as exc:
            logger.exception("AI analysis failed")

        return {"matches": web_matches}
    except Exception as exc:
        logger.exception("search/file failure")
        raise HTTPException(status_code=500, detail="search failed") from exc
