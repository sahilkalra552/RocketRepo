from typing import List
from fastapi import FastAPI, File, UploadFile
import shutil
import os
import asyncio
from titan_client import generate_titan_embedding
from opensearch_client import search_similar_skus

app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/process-skus/")
async def process_skus(files: List[UploadFile] = File(...)):
    tasks = [process_file(file) for file in files]
    results = await asyncio.gather(*tasks)  # Run all tasks concurrently
    return {"results": results}

async def process_file(file: UploadFile):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    # Save uploaded file asynchronously
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        embedding = await asyncio.to_thread(generate_titan_embedding, file_path)
        similar_skus = await asyncio.to_thread(search_similar_skus, embedding)

        os.remove(file_path)

        return {"filename": file.filename, "matches": similar_skus}

    except Exception as e:
        return {"filename": file.filename, "error": str(e)}


    
