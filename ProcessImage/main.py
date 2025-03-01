from typing import List

import cv2
from fastapi import FastAPI, File, UploadFile
import shutil
import os
from titan_client import generate_titan_embedding
from opensearch_client import search_similar_skus
from ultralytics import YOLO

app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

model = YOLO("../models/best_100epochs.pt")

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


@app.post("/process-skus/2")
async def process_skus2(file: UploadFile = File(...)):
    output_dir = "cropped_skus"
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join("uploads", file.filename)

    # Save uploaded file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # Load image
        image = cv2.imread(file_path)

        # Run YOLO object detection
        detections = model(image)[0]  # Get first frame of detections

        cropped_files = []
        for i, det in enumerate(detections.boxes.data):
            x1, y1, x2, y2, conf, cls = det.tolist()

            if conf >= 0:  # Confidence threshold
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                sku_crop = image[y1:y2, x1:x2]

                # Save cropped SKU image
                cropped_filename = f"sku_{i}_{file.filename}"
                cropped_path = os.path.join(output_dir, cropped_filename)
                cv2.imwrite(cropped_path, sku_crop)
                cropped_files.append(cropped_filename)

        os.remove(file_path)
        return {"filename": file.filename, "cropped_skus": cropped_files}

    except Exception as e:
        return {"filename": file.filename, "error": str(e)}