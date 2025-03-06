import pandas as pd
import json
import requests
from requests.auth import HTTPBasicAuth
import os

# Constants - update with your actual OpenSearch details
OPENSEARCH_ENDPOINT = "https://search-salescoderocket-kii3jxpcn5geqdden3zks76coa.aos.ap-south-1.on.aws"
INDEX_NAME = "ideal_skus"

# OpenSearch authentication
USERNAME = "applicate"
PASSWORD = "123Applicate$"

HEADERS = {"Content-Type": "application/json"}

# Paths
EXCEL_PATH = "/Users/satvikchaudhary/Desktop/Hackathon/IdealImagesInfoFinall.xlsx"
EMBEDDINGS_FILE = "/Users/satvikchaudhary/PycharmProjects/ProjectIR/configs/ideal_image_embeddings.json"

def load_metadata():
    """Load metadata from Excel into a lookup dictionary."""
    df = pd.read_excel(EXCEL_PATH, sheet_name="Table1", dtype=str)

    metadata = {}
    for _, row in df.iterrows():
        file_name = str(row["file_name"]).strip()  # Ensure no extra spaces
        metadata[file_name] = {
            "sku_code": row["sku_code"],
            "category": row["category"],
            "item_name": row["item_name"]
        }

    print(f"✅ Loaded {len(metadata)} items from Excel.")
    return metadata

def create_index():
    mapping = {
        "settings": {
            "index": {
                "knn": True
            }
        },
        "mappings": {
            "properties": {
                "sku_code": {"type": "keyword"},
                "item_name": {"type": "text"},
                "category": {"type": "keyword"},
                "image_s3_path": {"type": "keyword"},
                "embedding": {
                    "type": "knn_vector",
                    "dimension": 1024,  # Match the output dimension of Titan embeddings
                    "similarity": "l2"
                }
            }
        }
    }

    url = f"{OPENSEARCH_ENDPOINT}/{INDEX_NAME}"
    response = requests.put(url, auth=HTTPBasicAuth(USERNAME, PASSWORD), headers={"Content-Type": "application/json"}, json=mapping)
    print(f"Index creation response: {response.status_code}, {response.text}")


def ingest_embeddings(metadata):
    """Ingest all embeddings into OpenSearch with metadata."""
    with open(EMBEDDINGS_FILE, "r") as f:
        embeddings = json.load(f)

    total_count = 0
    success_count = 0

    for s3_path, embedding in embeddings.items():
        total_count += 1

        # Extract file name without extension from S3 path
        file_name_with_extension = os.path.basename(s3_path)
        file_name = os.path.splitext(file_name_with_extension)[0]

        if file_name not in metadata:
            print(f"⚠️ No metadata found for {file_name}, skipping...")
            continue

        # Construct document with metadata + embedding
        doc = {
            "sku_code": metadata[file_name]["sku_code"],
            "item_name": metadata[file_name]["item_name"],
            "category": metadata[file_name]["category"],
            "image_s3_path": f"s3://humanize-ai/TeamRocket/IdealImages/{file_name_with_extension}",
            "embedding": embedding
        }

        # Upload to OpenSearch
        doc_url = f"{OPENSEARCH_ENDPOINT}/{INDEX_NAME}/_doc"
        response = requests.post(doc_url, auth=HTTPBasicAuth(USERNAME, PASSWORD), headers=HEADERS, json=doc)

        if response.status_code in [200, 201]:
            print(f"✅ Indexed {doc['item_name']}")
            success_count += 1
        else:
            print(f"❌ Failed to index {file_name}: {response.status_code}, {response.text}")

    print(f"✅ Successfully indexed {success_count}/{total_count} items.")

if __name__ == "__main__":
    metadata = load_metadata()

    # Optional - Create Index (only the first time)
    # Uncomment if needed
    # create_index()

    ingest_embeddings(metadata)
