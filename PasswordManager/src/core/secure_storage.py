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
        self.key = None  # 派生出来的密钥（用于 Fernet）
        self.backend = default_backend()
        self.iterations = 100_000  # PBKDF2 迭代次数

    def initialize_master_key(self, password, salt=None):
        """
        初始化主密钥。首次设置主密码时生成新的 salt；登录时使用已保存的 salt。
        """
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
        return salt  # 返回 salt 以便保存

    def verify_password(self, password):
        """
        用当前 key 尝试解密测试数据验证密码是否正确。
        """
        try:
            # 尝试读取数据文件
            if not os.path.exists(self.config.data_path):
                return False

            with open(self.config.data_path, "r", encoding="utf-8") as f:
                encrypted = json.load(f)

            if "data" not in encrypted:
                return False

            fernet = Fernet(self.key)
            decrypted_json = fernet.decrypt(encrypted["data"].encode())
            json.loads(decrypted_json.decode("utf-8"))  # 尝试解析 JSON，验证成功
            return True

        except Exception as e:
            print(f"[验证失败] {str(e)}")
            return False

    def save_data(self, data: dict):
        """
        使用当前派生密钥加密并保存数据。
        """
        fernet = Fernet(self.key)
        raw_json = json.dumps(data).encode()
        encrypted = fernet.encrypt(raw_json).decode()

        with open(self.config.data_path, "w", encoding="utf-8") as f:
            json.dump({"data": encrypted}, f, ensure_ascii=False, indent=4)

    def load_data(self) -> dict:
        """
        读取并解密数据文件（使用当前派生密钥）。
        """
        if not os.path.exists(self.config.data_path):
            return {}

        with open(self.config.data_path, "r", encoding="utf-8") as f:
            encrypted = json.load(f)

        if "data" not in encrypted:
            return {}

        fernet = Fernet(self.key)
        decrypted = fernet.decrypt(encrypted["data"].encode())
        return json.loads(decrypted.decode("utf-8"))
