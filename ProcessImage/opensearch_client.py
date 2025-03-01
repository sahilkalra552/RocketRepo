import json
import requests
from requests.auth import HTTPBasicAuth
from config import OPENSEARCH_ENDPOINT, OPENSEARCH_INDEX, OPENSEARCH_USERNAME, OPENSEARCH_PASSWORD

def search_similar_skus(embedding, k=5):
    """Query OpenSearch for top K similar SKUs"""
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
    return [
        {
            "sku_code": result["_source"]["sku_code"],
            "item_name": result["_source"]["item_name"],
            "category": result["_source"]["category"],
            "image_s3_path": result["_source"]["image_s3_path"],
            "score": result["_score"]
        }
        for result in results
    ]
