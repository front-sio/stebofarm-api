import requests
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
import os
import json

# Load the private key
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRIVATE_KEY_PATH = os.path.join(BASE_DIR, "keys/private_key.pem")

with open(PRIVATE_KEY_PATH, "rb") as f:
    private_key = serialization.load_pem_private_key(f.read(), password=None)

# Unique key assigned to this frontend
UNIQUE_KEY = "replace_with_your_unique_key"  # Replace with the actual unique key provided by the backend

# Fetch the payload from the backend
API_URL = "http://127.0.0.1:8000/api/get_payload/"
response = requests.get(API_URL)

if response.status_code != 200:
    print(f"Failed to fetch payload: {response.status_code} {response.text}")
    exit(1)

payload = response.json()
payload_json = json.dumps(payload).encode("utf-8")

# Generate the signature
signature = private_key.sign(
    payload_json,
    padding.PKCS1v15(),
    hashes.SHA256(),
)

# Send the signed payload back to the backend
REGISTER_URL = "http://127.0.0.1:8000/api/users/register/"

headers = {
    "Content-Type": "application/json",
    "X-Signature": signature.hex(),
    "X-Unique-Key": UNIQUE_KEY,
}

response = requests.post(REGISTER_URL, headers=headers, data=payload_json)

print("Response:", response.status_code, response.json())
