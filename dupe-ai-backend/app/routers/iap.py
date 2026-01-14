from fastapi import APIRouter, Request

router = APIRouter(prefix="/iap", tags=["iap"])

@router.post("/asns")
async def app_store_notifications(request: Request):
    # Store raw JWS payload; add signature verify later.
    payload = await request.body()
    # TODO: persist and process into entitlements table
    return {"ok": True}

@router.get("/entitlements")
def entitlements():
    # TODO: derive from stored Apple status + current time
    return {"isPro": False, "expiresAt": None}
