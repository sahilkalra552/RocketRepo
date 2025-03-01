import boto3
import json
import base64
from config import AWS_REGION

# Initialize Bedrock client
bedrock = boto3.client("bedrock-runtime", region_name=AWS_REGION)

def generate_titan_embedding(image_path):
    """Generate Titan Multimodal Embedding for an image"""
    with open(image_path, "rb") as img_file:
        image_b64 = base64.b64encode(img_file.read()).decode("utf-8")

    payload = {
        "inputImage": image_b64
    }

    response = bedrock.invoke_model(
        modelId="amazon.titan-embed-image-v1",
        contentType="application/json",
        accept="application/json",
        body=json.dumps(payload)
    )

    result = json.loads(response['body'].read())
    return result['embedding']
