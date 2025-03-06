import boto3
import io
from PIL import Image

# Initialize Rekognition client
rekognition_client = boto3.client("rekognition", region_name="ap-south-1")

def extract_text_from_image(image_path: str):
    """Extracts text from image using Amazon Rekognition"""
    with open(image_path, "rb") as image_file:
        image_bytes = image_file.read()

    response = rekognition_client.detect_text(
        Image={'Bytes': image_bytes}
    )

    text_detections = response.get("TextDetections", [])
    extracted_text = [detection["DetectedText"].lower() for detection in text_detections if detection["Type"] == "LINE"]

    return extracted_text
