from typing import List

import cv2
from fastapi import FastAPI, File, UploadFile
import shutil
import os
from titan_client import generate_titan_embedding
from opensearch_client import search_similar_skus
from ultralytics import YOLO
import tempfile
import uuid
import numpy as np

app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

model = YOLO("../models/best_100epochs.pt")

@app.post("/process-skus/")
async def process_skus(file: UploadFile = File(...)):
    results = []
    cropped_images, cropped_files=getCroppedSkus(file)

    for image, file_path in zip(cropped_images, cropped_files):

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


def getCroppedSkus(file: UploadFile):
    unique_id = str(uuid.uuid4())  # Generate a unique ID
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        shutil.copyfileobj(file.file, temp_file)
        temp_file_path = temp_file.name

    image = cv2.imread(temp_file_path)
    os.remove(temp_file_path)

    detections = model(image)[0]  # Get first frame of detections

    output_dir = f"cropped_skus/{unique_id}"
    os.makedirs(output_dir, exist_ok=True)

    cropped_images = []
    cropped_files = []

    for i, det in enumerate(detections.boxes.data):
        x1, y1, x2, y2, conf, cls = det.tolist()

        if conf > 0.4:  # Confidence threshold
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            sku_crop = image[y1:y2, x1:x2]

            cropped_filename = f"sku_{i}_{unique_id}.jpg"
            cropped_path = os.path.join(output_dir, cropped_filename)
            cv2.imwrite(cropped_path, sku_crop)

            cropped_images.append(sku_crop)
            cropped_files.append(cropped_path)

    return cropped_images, cropped_files