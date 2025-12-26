from fastapi import FastAPI, UploadFile, File
from app.core_engine import DupeEngine
from app.database import SessionLocal, Product, init_db
from sqlalchemy import text
import io
from PIL import Image
import shutil

app = FastAPI()

# Load AI on startup
engine = DupeEngine()

# Initialize DB on startup
@app.on_event("startup")
def startup_db():
    init_db()

@app.post("/scan")
async def scan_look(file: UploadFile = File(...)):
    # 1. Save uploaded file temporarily
    temp_filename = f"temp_{file.filename}"
    with open(temp_filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # 2. Cut out clothes
    detected_items = engine.cut_clothes(temp_filename)
    
    if not detected_items:
        return {"message": "No clothes detected."}

    results = []
    db = SessionLocal()

    # 3. For each cut-out, find a match in DB
    for item in detected_items:
        # Convert image to vector
        query_vector = engine.get_vector(item["image"])
        
        # Search DB using pgvector (L2 Distance)
        # "<->" operator means "distance" in pgvector
        matches = db.query(Product).order_by(
            Product.embedding.l2_distance(query_vector)
        ).limit(3).all()
        
        item_matches = []
        for match in matches:
            item_matches.append({
                "name": match.name,
                "price": match.price,
                "image": match.image_url
            })
            
        results.append({
            "detected": item["label"],
            "matches": item_matches
        })
        
    db.close()
    return {"results": results}