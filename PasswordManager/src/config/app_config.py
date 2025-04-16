"""
@Author: Chan Sheen
@Date: 2025/4/15 17:12
@File: app_config.py
@Description: 
"""

import os
from pathlib import Path

class AppConfig:
    def __init__(self):
        self.config_dir = self._get_config_path()
        self.data_path = self.config_dir / "passwords.dat"
        self._ensure_directory()

    def _get_config_path(self):
        """获取配置目录路径"""
        if os.name == 'nt':  # Windows
            return Path(os.getenv('APPDATA')) / "PasswordManager"
        else:  # macOS/Linux
            return Path.home() / ".config" / "PasswordManager"

    def _ensure_directory(self):
        """确保配置目录存在"""
        os.makedirs(self.config_dir, exist_ok=True)
        print(f"配置目录: {self.config_dir}")
