import requests
from requests.auth import HTTPBasicAuth

OPENSEARCH_ENDPOINT = "https://search-salescoderocket-kii3jxpcn5geqdden3zks76coa.aos.ap-south-1.on.aws"
INDEX_NAME = "ideal_skus"
USERNAME = "applicate"
PASSWORD = "123Applicate$"

response = requests.delete(f"{OPENSEARCH_ENDPOINT}/{INDEX_NAME}", auth=HTTPBasicAuth(USERNAME, PASSWORD))

print(f"Delete response: {response.status_code}, {response.text}")
