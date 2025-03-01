import boto3
import json
import base64
import os


s3_client = boto3.client("s3")
bedrock = boto3.client("bedrock-runtime", region_name="ap-south-1")

bucket_name = "humanize-ai"
prefix = "TeamRocket/IdealImages/"

def list_images_in_s3():

    images = []
    response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    for item in response.get("Contents", []):
        if item['Key'].lower().endswith(('.png', '.jpg', '.jpeg')):
            images.append(item['Key'])
    return images

def get_image_embedding(s3_key):
    """Download image from S3, convert to base64, and get Titan embedding."""
    s3_object = s3_client.get_object(Bucket=bucket_name, Key=s3_key)
    image_data = s3_object['Body'].read()
    image_b64 = base64.b64encode(image_data).decode("utf-8")

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

def generate_and_save_embeddings():
    """Generate embeddings for all images and save to a JSON file."""
    embeddings = {}

    images = list_images_in_s3()
    print(f"Found {len(images)} images in S3 bucket.")

    for image_key in images:
        print(f"Processing {image_key}...")
        embedding = get_image_embedding(image_key)
        embeddings[image_key] = embedding

    with open("../configs/ideal_image_embeddings.json", "w") as f:
        json.dump(embeddings, f, indent=4)

    print("✅ Embeddings saved to ideal_image_embeddings.json")

if __name__ == "__main__":
    generate_and_save_embeddings()
