import requests
from requests.auth import HTTPBasicAuth

# Configuration - replace these with your actual values
OPENSEARCH_ENDPOINT = "https://search-salescoderocket-kii3jxpcn5geqdden3zks76coa.aos.ap-south-1.on.aws"  # e.g., https://search-your-cluster.region.es.amazonaws.com
INDEX_NAME = "ideal_skus"  # Your actual index name
USERNAME = "applicate"
PASSWORD = "123Applicate$"

# Get the mappings for the index
url = f"{OPENSEARCH_ENDPOINT}/{INDEX_NAME}/_mapping"
response = requests.get(url, auth=HTTPBasicAuth(USERNAME, PASSWORD))

# Print the current mappings
if response.status_code == 200:
    print("✅ Current Index Mapping:")
    print(response.json())
else:
    print(f"❌ Failed to fetch index mappings: {response.status_code}")
    print(response.text)
