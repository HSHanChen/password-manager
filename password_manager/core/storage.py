
"""
@Author: Henve
@Date: 2025/4/14 11:52
@File: storage.py
@Description: 数据读取保存逻辑
"""
import os
import json
from core.crypto import encrypt_data, decrypt_data

# 加密存储的文件路径
DATA_FILE = os.path.join("data", "passwords.enc")

def save_data(data: list, master_password: str):
    """
    将密码数据加密后保存到文件
    """
    encrypted = encrypt_data(json.dumps(data), master_password)
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "wb") as f:
        f.write(encrypted)

def load_data(master_password: str) -> list:
    """
    加载并解密密码数据
    """
    if not os.path.exists(DATA_FILE):
        return []  # 如果文件不存在，表示第一次运行，返回空列表
    with open(DATA_FILE, "rb") as f:
        encrypted = f.read()
    decrypted = decrypt_data(encrypted, master_password)
    return json.loads(decrypted)

