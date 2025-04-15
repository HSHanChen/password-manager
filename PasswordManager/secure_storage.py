"""
@Author: Chan Sheen
@Date: 2025/4/15 16:21
@File: secure_storage.py
@Description: 
"""
import os
import json
import base64
import hashlib
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad


class SecureStorage:
    def __init__(self, config):
        self.config = config
        os.makedirs(self.config.data_path.parent, exist_ok=True)

    def set_master_key(self, password, salt=None):
        """设置主密钥"""
        self.salt = salt if salt else get_random_bytes(16)
        self.master_key = PBKDF2(password.encode(), self.salt, dkLen=32, count=100000)
        return self.salt

    def encrypt_data(self, data):
        """加密数据"""
        iv = get_random_bytes(16)
        cipher = AES.new(self.master_key, AES.MODE_CBC, iv)
        padded_data = pad(json.dumps(data).encode(), AES.block_size)
        encrypted = cipher.encrypt(padded_data)
        return base64.b64encode(self.salt + iv + encrypted).decode()

    def decrypt_data(self, encrypted_str):
        """解密数据"""
        try:
            data = base64.b64decode(encrypted_str.encode())
            salt, iv, encrypted = data[:16], data[16:32], data[32:]
            cipher = AES.new(self.master_key, AES.MODE_CBC, iv)
            decrypted = unpad(cipher.decrypt(encrypted), AES.block_size)
            return json.loads(decrypted.decode())
        except Exception as e:
            raise RuntimeError(f"解密失败: {str(e)}")

    def save_data(self, data):
        """保存加密数据"""
        with open(self.config.data_path, 'w') as f:
            f.write(self.encrypt_data(data))

    def load_data(self):
        """加载数据"""
        if not os.path.exists(self.config.data_path):
            return {
                "passwords": [],
                "categories": [{"id": 1, "name": "默认分类", "parent_id": None}],
                "master_salt": None
            }

        with open(self.config.data_path, 'r') as f:
            return self.decrypt_data(f.read())

    def verify_password(self, password, stored_salt):
        """验证密码"""
        temp_key = PBKDF2(password.encode(), stored_salt, dkLen=32, count=100000)
        return hashlib.sha256(temp_key).digest()