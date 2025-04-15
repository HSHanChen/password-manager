"""
@Author: Chan Sheen
@Date: 2025/4/15 16:21
@File: config.py
@Description: 
"""
import os
import json
from pathlib import Path


class AppConfig:
    def __init__(self):
        self.config_path = self.get_appdata_path() / "config.json"
        self.default_data_dir = self.get_appdata_path() / "pwdManager"
        self.data_path = self.default_data_dir / "passwords.dat"

        # 初始化配置目录
        os.makedirs(self.default_data_dir, exist_ok=True)

        # 加载现有配置
        self.load_config()

    def get_appdata_path(self):
        """获取系统AppData路径"""
        if os.name == 'nt':  # Windows
            return Path(os.getenv('APPDATA'))
        else:  # macOS/Linux
            return Path.home() / '.config'

    def load_config(self):
        """加载配置文件"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    custom_path = config.get('data_path')
                    if custom_path and os.path.exists(custom_path):
                        self.data_path = Path(custom_path)
            except:
                pass

    def save_config(self, data_path=None):
        """保存配置"""
        config = {
            'data_path': str(data_path) if data_path else None
        }
        with open(self.config_path, 'w') as f:
            json.dump(config, f)

        if data_path:
            self.data_path = Path(data_path)