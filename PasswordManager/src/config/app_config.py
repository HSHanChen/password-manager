"""
@Author: Chan Sheen
@Date: 2025/4/15 17:12
@File: app_config.py
@Description: 
"""
import json
import os
from pathlib import Path


class AppConfig:
    def __init__(self):
        self.config_dir = self.get_config_path()
        self.config_path = self.config_dir / "config.json"
        self.default_data_path = self.config_dir / "passwords.dat"
        self.data_path = self.default_data_path

        os.makedirs(self.config_dir, exist_ok=True)
        self.load_config()

    def get_config_path(self):
        if os.name == 'nt':
            return Path(os.getenv('APPDATA')) / "PasswordManager"
        else:
            return Path.home() / ".config" / "PasswordManager"

    def load_config(self):
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    if config.get("data_path"):
                        self.data_path = Path(config["data_path"])
            except:
                pass

    def save_config(self, data_path=None):
        config = {"data_path": str(data_path)} if data_path else {}
        with open(self.config_path, 'w') as f:
            json.dump(config, f)
        if data_path:
            self.data_path = Path(data_path)
