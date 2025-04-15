"""
@Author: Henve
@Date: 2025/4/15 14:34
@File: crypto.py
@Description: 
"""

import os
import hashlib
from base64 import b64encode, b64decode
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes


class CryptoUtils:
    def __init__(self):
        self.salt = None
        self.master_key = None

    def set_master_key(self, password: str, salt: bytes = None) -> bytes:
        """Derive master key from password"""
        if salt is None:
            self.salt = get_random_bytes(16)
        else:
            self.salt = salt

        self.master_key = PBKDF2(
            password.encode('utf-8'),
            self.salt,
            dkLen=32,  # 256-bit key
            count=100000  # PBKDF2 iteration count
        )
        return self.salt

    def verify_master_password(self, password: str, salt: bytes, stored_hash: bytes) -> bool:
        """Verify if the provided password matches the stored master password"""
        key = PBKDF2(
            password.encode('utf-8'),
            salt,
            dkLen=32,
            count=100000
        )
        # Hash the key for storage verification
        hashed_key = hashlib.sha256(key).digest()
        return hashed_key == stored_hash

    def encrypt_password(self, plaintext: str) -> bytes:
        """Encrypt a password using AES-GCM"""
        if not self.master_key:
            raise ValueError("Master key not set")

        iv = get_random_bytes(12)  # 96-bit IV for GCM
        cipher = AES.new(self.master_key, AES.MODE_GCM, nonce=iv)
        ciphertext, tag = cipher.encrypt_and_digest(plaintext.encode('utf-8'))

        # Combine IV + tag + ciphertext
        encrypted_data = iv + tag + ciphertext
        return encrypted_data

    def decrypt_password(self, encrypted_data: bytes) -> str:
        """Decrypt a password using AES-GCM"""
        if not self.master_key:
            raise ValueError("Master key not set")

        if len(encrypted_data) < 28:  # IV(12) + tag(16)
            raise ValueError("Invalid encrypted data")

        iv = encrypted_data[:12]
        tag = encrypted_data[12:28]
        ciphertext = encrypted_data[28:]

        cipher = AES.new(self.master_key, AES.MODE_GCM, nonce=iv)
        plaintext = cipher.decrypt_and_verify(ciphertext, tag)
        return plaintext.decode('utf-8')

    def hash_for_storage(self, key: bytes) -> bytes:
        """Create a hash of the master key for storage"""
        return hashlib.sha256(key).digest()