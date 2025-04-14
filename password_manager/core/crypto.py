"""
@Author: Henve
@Date: 2025/4/14 11:52
@File: crypto.py
@Description: 加密解密逻辑
"""

from cryptography.fernet import Fernet
import hashlib
import base64

def get_key(password: str) -> bytes:
    digest = hashlib.sha256(password.encode()).digest()
    return base64.urlsafe_b64encode(digest)

def encrypt_data(data: str, password: str) -> bytes:
    """
    接收一个字符串（比如 JSON），返回加密后的字节数据
    """
    fernet = Fernet(get_key(password))
    return fernet.encrypt(data.encode())

def decrypt_data(token: bytes, password: str) -> str:
    """
    接收加密的字节数据，返回解密后的字符串（比如 JSON 字符串）
    """
    fernet = Fernet(get_key(password))
    return fernet.decrypt(token).decode()

