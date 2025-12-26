from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse
from sqlalchemy import text
from app.database import engine as db_engine, SessionLocal, init_db

app = FastAPI(title="DUPE.AI Backend", version="0.1.0")

# Allow your iOS app / local dev origins as needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def _startup():
    # Ensure DB + pgvector are ready and tables exist
    init_db()

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs", status_code=302)

@app.get("/_health")
def health():
    # Check DB connectivity and 'vector' extension presence
    with db_engine.connect() as conn:
        conn.execute(text("SELECT 1;"))
        # if this errors, extension isn't there
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
    return {"ok": True}

@app.post("/scan")
async def scan_look(file: UploadFile = File(...)):
    # Temp stub so we can verify uploads work end-to-end on Railway
    name = file.filename
    size = 0
    async for chunk in file.stream():
        size += len(chunk)
    return {"received": name, "bytes": size}
