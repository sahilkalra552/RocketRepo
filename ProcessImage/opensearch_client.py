import json
import requests
from requests.auth import HTTPBasicAuth
from difflib import SequenceMatcher
from config import OPENSEARCH_ENDPOINT, OPENSEARCH_INDEX, OPENSEARCH_USERNAME, OPENSEARCH_PASSWORD


def calculate_text_similarity(text1: str, text2: str) -> float:
    """Calculate text similarity between two strings using SequenceMatcher."""
    return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()


def search_top_sku_with_text_matching(embedding, detected_text_list, k=5):
    """Search OpenSearch for top K similar SKUs and apply text matching."""

    search_url = f"{OPENSEARCH_ENDPOINT}/{OPENSEARCH_INDEX}/_search"

    query = {
        "size": k,
        "query": {
            "knn": {
                "embedding": {
                    "vector": embedding,
                    "k": k
                }
            }
        },
        "_source": ["sku_code", "item_name", "category", "image_s3_path"]
    }

    response = requests.post(
        search_url,
        auth=HTTPBasicAuth(OPENSEARCH_USERNAME, OPENSEARCH_PASSWORD),
        headers={"Content-Type": "application/json"},
        data=json.dumps(query)
    )

    if response.status_code != 200:
        raise Exception(f"Failed to query OpenSearch: {response.status_code}\n{response.text}")

    results = response.json().get("hits", {}).get("hits", [])

    final_results = []
    user_image_extracted_text = " ".join(detected_text_list)
    for result in results:
        item_name = result["_source"]["item_name"]

        ocr_similarity = calculate_text_similarity(item_name, user_image_extracted_text)
        final_results.append({
            "sku_code": result["_source"]["sku_code"],
            "item_name": item_name,
            "category": result["_source"]["category"],
            "image_s3_path": result["_source"]["image_s3_path"],
            "score": result["_score"],
            "ocr_similarity": ocr_similarity,
            "ocr_detected_text": user_image_extracted_text
        })

    return final_results
