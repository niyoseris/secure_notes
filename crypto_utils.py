import os
import hashlib
import base64
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# Constants
SALT_FOLDER = b"secure_notes_folder_salt_v1"
SALT_KEY = b"secure_notes_encryption_key_salt_v1"
ITERATIONS = 100_000

def derive_folder_id(phrase: str, pin: str) -> str:
    """
    Derives a deterministic folder ID from the phrase and pin.
    This ID is used to locate the user's storage directory.
    It does NOT reveal the key.
    """
    data = f"{phrase}|{pin}".encode('utf-8')
    # Using SHA256 for a consistent filename safe hash
    hasher = hashlib.sha256()
    hasher.update(data)
    hasher.update(SALT_FOLDER)
    return hasher.hexdigest()

def derive_encryption_key(phrase: str, pin: str) -> bytes:
    """
    Derives the AES-GCM encryption key from the phrase and pin.
    This key is NEVER stored on disk.
    """
    password = f"{phrase}|{pin}".encode('utf-8')
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32, # AES-256
        salt=SALT_KEY,
        iterations=ITERATIONS,
        backend=default_backend()
    )
    return kdf.derive(password)

def encrypt_content(content: str, key: bytes) -> bytes:
    """
    Encrypts the content using AES-GCM.
    Returns: nonce + ciphertext + tag (handled by AESGCM)
    """
    aesgcm = AESGCM(key)
    nonce = os.urandom(12) # NIST recommended nonce size for GCM
    data = content.encode('utf-8')
    ciphertext = aesgcm.encrypt(nonce, data, None)
    return nonce + ciphertext

def decrypt_content(encrypted_data: bytes, key: bytes) -> str:
    """
    Decrypts the content using AES-GCM.
    Raises InvalidTag if decryption fails.
    """
    aesgcm = AESGCM(key)
    nonce = encrypted_data[:12]
    ciphertext = encrypted_data[12:]
    plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    return plaintext.decode('utf-8')
