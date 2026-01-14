import httpx
from app.config import settings
from loguru import logger
from typing import List, Dict, Any

async def search_by_image(image_url: str) -> List[Dict[str, Any]]:
    """
    Uses SerpApi's Google Lens API to find visually similar products.
    """
    if not settings.SERPAPI_KEY:
        logger.warning("SERPAPI_KEY not set")
        return []

    params = {
        "engine": "google_lens",
        "url": image_url,
        "api_key": settings.SERPAPI_KEY
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get("https://serpapi.com/search", params=params, timeout=30.0)
            response.raise_for_status()
            data = response.json()
            
            # Extract visual matches
            visual_matches = data.get("visual_matches", [])
            results = []
            
            for match in visual_matches:
                results.append({
                    "name": match.get("title"),
                    "source": match.get("source"),
                    "price": match.get("price", {}).get("extracted_value"),
                    "currency": match.get("price", {}).get("currency"),
                    "image_url": match.get("thumbnail"),
                    "buy_url": match.get("link"),
                    "is_replica": "aliexpress" in match.get("link", "").lower() or "dhgate" in match.get("link", "").lower()
                })
            
            return results
        except Exception as e:
            logger.error(f"SerpApi search failed: {e}")
            return []
