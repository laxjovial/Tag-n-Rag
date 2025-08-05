import os
from cryptography.fernet import Fernet

# Load the encryption key from environment variables
# This key must be 32 url-safe base64-encoded bytes.
# Generate one with: Fernet.generate_key()
ENCRYPTION_KEY = os.environ.get("FERNET_KEY")
if not ENCRYPTION_KEY:
    raise ValueError("No FERNET_KEY set for encryption. Please set it in your .env file.")

fernet = Fernet(ENCRYPTION_KEY.encode())

def encrypt_credentials(credentials: str) -> bytes:
    """Encrypts a string (e.g., JSON credentials) into bytes."""
    return fernet.encrypt(credentials.encode('utf-8'))

def decrypt_credentials(encrypted_credentials: bytes) -> str:
    """Decrypts bytes back into a string."""
    return fernet.decrypt(encrypted_credentials).decode('utf-8')
