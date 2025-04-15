"""
@Author: Chan Sheen
@Date: 2025/4/15 16:21
@File: secure_storage.py
@Description: 
"""
import base64
import hashlib
import json
import os

from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad


class SecureStorage:
    def __init__(self, config):
        self.config = config
        self.salt = None
        self.master_key = None
        os.makedirs(self.config.data_path.parent, exist_ok=True)

    def set_master_key(self, password, salt=None):
        self.salt = salt if salt else get_random_bytes(16)
        self.master_key = PBKDF2(password.encode(), self.salt, dkLen=32, count=100000)
        return self.salt

    def encrypt_data(self, data):
        iv = get_random_bytes(16)
        cipher = AES.new(self.master_key, AES.MODE_CBC, iv)
        encrypted = cipher.encrypt(pad(json.dumps(data).encode(), AES.block_size))
        return base64.b64encode(self.salt + iv + encrypted).decode()

    def decrypt_data(self, encrypted_str):
        data = base64.b64decode(encrypted_str.encode())
        salt, iv, encrypted = data[:16], data[16:32], data[32:]
        cipher = AES.new(self.master_key, AES.MODE_CBC, iv)
        return json.loads(unpad(cipher.decrypt(encrypted), AES.block_size).decode())

    def save_data(self, data):
        with open(self.config.data_path, 'w') as f:
            f.write(self.encrypt_data(data))

    def load_data(self):
        if not os.path.exists(self.config.data_path):
            return {"passwords": [], "categories": [], "master_salt": None}
        with open(self.config.data_path, 'r') as f:
            return self.decrypt_data(f.read())

    def verify_password(self, password, salt):
        key = PBKDF2(password.encode(), salt, dkLen=32, count=100000)
        return hashlib.sha256(key).digest()
