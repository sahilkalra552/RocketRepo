from typing import List
from fastapi import FastAPI, File, UploadFile
import shutil
import os
import asyncio
from titan_client import generate_titan_embedding
from opensearch_client import search_top_sku_with_text_matching
from text_extractor import extract_text_from_image

app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/process-skus/")
async def process_skus(files: List[UploadFile] = File(...)):
    tasks = [process_file(file) for file in files]
    results = await asyncio.gather(*tasks)
    return {"results": [res for res in results if res is not None]}


async def process_file(file: UploadFile):
    """Process a single file asynchronously."""
    if not file.filename:
        return None

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    await save_file(file, file_path)

    try:
        # Step 1 - Generate Titan Embedding
        embedding = await asyncio.to_thread(generate_titan_embedding, file_path)

        # Step 2 - Extract text using Amazon Rekognition OCR
        detected_text = await asyncio.to_thread(extract_text_from_image, file_path)

        # Step 3 - Search OpenSearch for top SKU and match text
        matched_sku = await asyncio.to_thread(search_top_sku_with_text_matching, embedding, detected_text)

        os.remove(file_path)

        return {
            "filename": file.filename,
            "detected_text": detected_text,
            "matched_sku": matched_sku
        }

    except Exception as e:
        return {
            "filename": file.filename,
            "error": str(e)
        }

async def save_file(file: UploadFile, file_path: str):
    """Save the uploaded file asynchronously."""
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return file_path

