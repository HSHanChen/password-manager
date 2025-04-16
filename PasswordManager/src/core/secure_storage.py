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

        # 初始化时尝试加载salt
        if os.path.exists(self.config.data_path):
            with open(self.config.data_path, 'r') as f:
                content = f.read()
                if content:
                    data = base64.b64decode(content.encode())
                    self.salt = data[:16]

    def initialize_master_key(self, password, salt=None):
        """初始化主密钥"""
        self.salt = salt if salt else get_random_bytes(16)
        self.master_key = PBKDF2(
            password.encode(),
            self.salt,
            dkLen=32,
            count=100000
        )
        return self.salt

    def encrypt_data(self, data):
        """加密数据"""
        if not self.master_key:
            raise ValueError("主密钥未初始化")

        iv = get_random_bytes(16)
        cipher = AES.new(self.master_key, AES.MODE_CBC, iv)
        encrypted = cipher.encrypt(pad(json.dumps(data).encode(), AES.block_size))
        return base64.b64encode(self.salt + iv + encrypted).decode()

    def decrypt_data(self, encrypted_str):
        """解密数据"""
        if not self.master_key:
            raise ValueError("主密钥未初始化")

        data = base64.b64decode(encrypted_str.encode())
        salt, iv, encrypted = data[:16], data[16:32], data[32:]

        if salt != self.salt:
            raise ValueError("Salt不匹配")

        cipher = AES.new(self.master_key, AES.MODE_CBC, iv)
        decrypted = unpad(cipher.decrypt(encrypted), AES.block_size)
        return json.loads(decrypted.decode())

    def save_data(self, data):
        print("准备保存数据...")  # 调试
        try:
            if "master_salt" not in data:
                data["master_salt"] = self.salt.hex()

            encrypted = self.encrypt_data(data)
            print(f"加密后的数据长度: {len(encrypted)}")  # 调试

            with open(self.config.data_path, 'w') as f:
                f.write(encrypted)
            print("数据保存成功")  # 调试
            return True
        except Exception as e:
            print(f"保存数据出错: {str(e)}")  # 调试
            raise

    def load_data(self):
        """从文件加载数据"""
        if not os.path.exists(self.config.data_path) or os.path.getsize(self.config.data_path) == 0:
            return {"passwords": [], "categories": [], "master_salt": None}

        with open(self.config.data_path, 'r') as f:
            content = f.read()
            if not content:
                return {"passwords": [], "categories": [], "master_salt": None}
            return self.decrypt_data(content)

    def verify_password(self, password):
        """修正后的密码验证方法"""
        try:
            data = self.load_data()
            if not data or not data.get("master_salt"):
                return False

            # 从文件读取存储的salt(hex字符串)
            file_salt_hex = data["master_salt"]
            file_salt = bytes.fromhex(file_salt_hex)

            # 用文件salt生成密钥
            file_key = PBKDF2(password.encode(), file_salt, dkLen=32, count=100000)
            file_hash = hashlib.sha256(file_key).digest()

            # 用当前salt生成密钥
            current_key = PBKDF2(password.encode(), self.salt, dkLen=32, count=100000)
            current_hash = hashlib.sha256(current_key).digest()

            # 双重验证
            return file_hash == current_hash
        except Exception as e:
            print(f"密码验证出错: {str(e)}")
            return False

    def save_data(self, data):
        """确保保存时包含完整的验证信息"""
        if "master_salt" not in data:
            data["master_salt"] = self.salt.hex()

        encrypted = self.encrypt_data(data)
        with open(self.config.data_path, 'wb') as f:  # 使用二进制写入
            f.write(encrypted.encode())
