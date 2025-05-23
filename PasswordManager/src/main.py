"""
@Author: Chan Sheen
@Date: 2025/4/15 16:20
@File: main.py
@Description: 
"""


import os
import sys

from PyQt6.QtWidgets import QApplication, QMessageBox, QDialog

from config.app_config import AppConfig
from core.secure_storage import SecureStorage
from ui.dialogs.login import LoginDialog
from ui.main_window import MainWindow


class PasswordManager:
    def __init__(self):
        self.config = AppConfig()
        self.ensure_config_directory()
        self.storage = SecureStorage(self.config)
        self.app = QApplication(sys.argv)
        self.main_window = None
        self.initialized = False

    def ensure_config_directory(self):
        """确保配置目录和密码文件路径存在"""
        os.makedirs(os.path.dirname(self.config.data_path), exist_ok=True)

    def run(self):
        # 加载样式表
        self.app.setStyleSheet(self.load_stylesheet())

        try:
            if not os.path.exists(self.config.data_path) or os.path.getsize(self.config.data_path) == 0:
                print("首次运行，需要设置主密码")
                self.setup_master_password()
            else:
                print("非首次运行，需要登录")
                self.login()

            if self.initialized and self.main_window:
                sys.exit(self.app.exec())
            else:
                sys.exit(1)

        except Exception as e:
            QMessageBox.critical(None, "错误", f"程序崩溃: {str(e)}")
            print(f"错误详情: {str(e)}")
            sys.exit(1)

    def setup_master_password(self):
        dialog = LoginDialog(mode='setup', crypto=self.storage)
        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            password = dialog.password_input.text()
            if not password:
                QMessageBox.warning(None, "提示", "密码不能为空。")
                return

            try:
                salt = self.storage.initialize_master_key(password)
                initial_data = {
                    "passwords": [],
                    "categories": [{"id": 1, "name": "默认分类", "parent_id": None}],
                    "master_salt": salt.hex()
                }
                self.storage.save_data(initial_data)
                self.initialized = True
                self.show_main_window()
            except Exception as e:
                print(f"设置密码出错: {str(e)}")
                QMessageBox.critical(None, "错误", f"密码设置失败: {str(e)}")
        else:
            print("用户取消设置密码")

    def login(self):
        dialog = LoginDialog(mode='login', crypto=self.storage)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            password = dialog.password_input.text()
            if not password:
                QMessageBox.warning(None, "提示", "密码不能为空。")
                return

            data = self.storage.load_data()
            if not data or not data.get("master_salt"):
                QMessageBox.critical(None, "错误", "数据损坏，找不到主密码记录。")
                return

            try:
                stored_salt = bytes.fromhex(data["master_salt"])
                self.storage.initialize_master_key(password, stored_salt)

                if self.storage.verify_password(password):
                    self.initialized = True
                    self.show_main_window()
                else:
                    QMessageBox.warning(None, "错误", "密码不正确。")
            except Exception as e:
                QMessageBox.critical(None, "错误", f"验证失败: {str(e)}")

    def show_main_window(self):
        try:
            self.main_window = MainWindow(self.storage, self.config)
            self.main_window.show()
        except Exception as e:
            print(f"主窗口创建失败: {str(e)}")
            QMessageBox.critical(None, "错误", f"无法启动主界面: {str(e)}")

    def load_stylesheet(self):
        try:
            # 注意根据项目结构调整路径
            with open("../resources/qss/main.qss", "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            print("样式表未找到")
            return ""


if __name__ == "__main__":
    manager = PasswordManager()
    manager.run()
