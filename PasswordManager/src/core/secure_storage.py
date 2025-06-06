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

    def is_master_password_set(self) -> bool:
        """
        判断是否已经设置了主密码（即 passwords.dat 文件是否存在且包含 salt 和 data 字段）
        """
        if not os.path.exists(self.config.data_path):
            return False

        try:
            with open(self.config.data_path, "r", encoding="utf-8") as f:
                obj = json.load(f)
            return "salt" in obj and "data" in obj
        except Exception as e:
            print(f"[读取主密码失败] {e}")
            return False

    def initialize_master_key(self, password, salt=None):
        if not password:
            raise ValueError("密码不能为空")

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
        if not self.key:
            raise ValueError("未初始化密钥，不能保存数据")

        fernet = Fernet(self.key)
        encrypted = fernet.encrypt(json.dumps(data).encode()).decode()

        obj = {
            "salt": data.get("master_salt"),
            "data": encrypted
        }

        with open(self.config.data_path, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False, indent=4)

    def load_data(self) -> dict:
        if not os.path.exists(self.config.data_path):
            return {}

        with open(self.config.data_path, "r", encoding="utf-8") as f:
            obj = json.load(f)

        if "data" not in obj:
            return {}

        if not self.key:
            raise ValueError("密钥未初始化，无法解密")

        fernet = Fernet(self.key)
        decrypted = fernet.decrypt(obj["data"].encode())
        return json.loads(decrypted.decode("utf-8"))
