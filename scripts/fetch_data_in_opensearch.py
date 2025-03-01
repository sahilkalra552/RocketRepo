import requests
from requests.auth import HTTPBasicAuth
import json


OPENSEARCH_ENDPOINT = "https://search-salescoderocket-kii3jxpcn5geqdden3zks76coa.aos.ap-south-1.on.aws"  # Replace with your OpenSearch endpoint
INDEX_NAME = "ideal_skus"
USERNAME = "applicate"
PASSWORD = "123Applicate$"


def fetch_all_documents():
    search_url = f"{OPENSEARCH_ENDPOINT}/{INDEX_NAME}/_search"


    query = {
        "size": 1000,
        "query": {"match_all": {}},
        "_source": ["sku_code", "item_name", "category", "image_s3_path"]
    }

    response = requests.get(
        search_url,
        auth=HTTPBasicAuth(USERNAME, PASSWORD),
        headers={"Content-Type": "application/json"},
        data=json.dumps(query)
    )

    if response.status_code != 200:
        print(f" Failed to fetch data: {response.status_code}\n{response.text}")
        return

    results = response.json()
    hits = results.get("hits", {}).get("hits", [])
    total_count = len(hits)

    print(f" Found {total_count} documents in index '{INDEX_NAME}'\n")

    # Print each document (excluding embeddings)
    for doc in hits:
        source = doc["_source"]
        print(json.dumps(source, indent=4))

    print(f" Total Documents in Index: {total_count}")


if __name__ == "__main__":
    fetch_all_documents()
