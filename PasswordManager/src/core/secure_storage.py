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

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class SecureStorage:
    def __init__(self, config):
        self.config = config
        self.key = None
        self.backend = default_backend()
        self.iterations = 100_000

    def initialize_master_key(self, password, salt=None):
        if salt is None:
            salt = os.urandom(16)

        kdf = PBKDF2HMAC(
            algorithm=hashlib.sha256(),
            length=32,
            salt=salt,
            iterations=self.iterations,
            backend=self.backend
        )
        self.key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return salt

    def verify_password(self, password):
        try:
            if not os.path.exists(self.config.data_path):
                return False

            with open(self.config.data_path, "r", encoding="utf-8") as f:
                obj = json.load(f)

            if "salt" not in obj or "data" not in obj:
                return False

            salt = bytes.fromhex(obj["salt"])
            self.initialize_master_key(password, salt)

            fernet = Fernet(self.key)
            decrypted = fernet.decrypt(obj["data"].encode())
            json.loads(decrypted.decode("utf-8"))
            return True

        except Exception as e:
            print(f"[验证失败] {str(e)}")
            return False

    def save_data(self, data: dict):
        fernet = Fernet(self.key)
        raw_json = json.dumps(data).encode()
        encrypted = fernet.encrypt(raw_json).decode()

        obj = {
            "salt": data.get("master_salt"),  # 这个必须是 hex 字符串
            "data": encrypted
        }

        with open(self.config.data_path, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False, indent=4)

    def load_data(self) -> dict:
        if not os.path.exists(self.config.data_path):
            return {}

        with open(self.config.data_path, "r", encoding="utf-8") as f:
            obj = json.load(f)

        if "salt" not in obj or "data" not in obj:
            return {}

        fernet = Fernet(self.key)
        decrypted = fernet.decrypt(obj["data"].encode())
        return json.loads(decrypted.decode("utf-8"))
