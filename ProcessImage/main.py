from typing import List
from fastapi import FastAPI, File, UploadFile
import shutil
import os
from titan_client import generate_titan_embedding
from opensearch_client import search_similar_skus

app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/process-skus/")
async def process_skus(files: List[UploadFile] = File(...)):


    results = []

    for file in files:
        file_path = os.path.join(UPLOAD_DIR, file.filename)

        # Save uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        try:
            embedding = generate_titan_embedding(file_path)
            similar_skus = search_similar_skus(embedding)
            os.remove(file_path)

            results.append({
                "filename": file.filename,
                "matches": similar_skus
            })

        except Exception as e:
            results.append({
                "filename": file.filename,
                "error": str(e)
            })

    return {"results": results}
