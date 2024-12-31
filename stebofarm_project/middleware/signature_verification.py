import os
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from django.http import JsonResponse
from users.models import FrontendApp

# Load public key
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUBLIC_KEY_PATH = os.path.join(BASE_DIR, "keys/public_key.pem")

with open(PUBLIC_KEY_PATH, "rb") as f:
    public_key = serialization.load_pem_public_key(f.read())

class SignatureVerificationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip certain paths
        if request.path.startswith("/admin/") or request.path.startswith("/static/"):
            return self.get_response(request)

        # Verify the unique key
        unique_key = request.headers.get("X-Unique-Key")
        if not unique_key or not FrontendApp.objects.filter(unique_key=unique_key).exists():
            return JsonResponse({"error": "Invalid or missing unique key"}, status=403)

        # Verify the signature
        signature = request.headers.get("X-Signature")
        if not signature:
            return JsonResponse({"error": "Missing signature"}, status=403)

        try:
            payload = request.body
            public_key.verify(
                bytes.fromhex(signature),
                payload,
                padding.PKCS1v15(),
                hashes.SHA256(),
            )
        except Exception as e:
            return JsonResponse({"error": "Invalid signature", "details": str(e)}, status=403)

        return self.get_response(request)
