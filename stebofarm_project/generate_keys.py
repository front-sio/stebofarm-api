from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

# Generate private (secret) key
private_key = rsa.generate_private_key(
    public_exponent=65537,  # Standard value for RSA keys
    key_size=2048,          # Key size in bits
    backend=default_backend()
)

# Serialize private key to PEM format
private_key_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.TraditionalOpenSSL,
    encryption_algorithm=serialization.NoEncryption()  # No password
)

# Write private key to a file
with open("keys/private_key.pem", "wb") as f:
    f.write(private_key_pem)

# Generate corresponding public key
public_key = private_key.public_key()

# Serialize public key to PEM format
public_key_pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

# Write public key to a file
with open("keys/public_key.pem", "wb") as f:
    f.write(public_key_pem)

print("Keys generated successfully: 'private_key.pem' and 'public_key.pem'")
