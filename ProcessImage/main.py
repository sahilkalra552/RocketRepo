from typing import List
from fastapi import FastAPI, File, UploadFile
import shutil
import os
from titan_client import generate_titan_embedding
from opensearch_client import search_top_sku_with_text_matching
from text_extractor import extract_text_from_image

app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/process-skus/")
async def process_skus(files: List[UploadFile] = File(...)):
    results = []

    for file in files:
        if not file.filename:
            continue
        file_path = os.path.join(UPLOAD_DIR, file.filename)

        # Save uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        try:
            # Step 1 - Generate Titan Embedding
            embedding = generate_titan_embedding(file_path)

            # Step 2 - Extract text using Amazon Rekognition OCR
            detected_text = extract_text_from_image(file_path)

            # Step 3 - Search OpenSearch for top SKU and match text
            matched_sku = search_top_sku_with_text_matching(embedding, detected_text)

            os.remove(file_path)

            results.append({
                "filename": file.filename,
                "detected_text": detected_text,
                "matched_sku": matched_sku
            })

        except Exception as e:
            results.append({
                "filename": file.filename,
                "error": str(e)
            })

    return {"results": results}
