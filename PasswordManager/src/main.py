"""
@Author: Chan Sheen
@Date: 2025/4/15 16:20
@File: main.py
@Description: 
"""

import os
import sys

from PyQt5.QtWidgets import QApplication, QMessageBox, QDialog

from config.app_config import AppConfig
from core.secure_storage import SecureStorage
from ui.dialogs.login import LoginDialog
from ui.main_window import MainWindow


class PasswordManager:
    def __init__(self):
        self.config = AppConfig()
        self.storage = SecureStorage(self.config)
        self.app = QApplication(sys.argv)
        self.main_window = None
        self.initialized = False

    def run(self):
        try:
            # 检查是否首次运行
            if not os.path.exists(self.config.data_path) or os.path.getsize(self.config.data_path) == 0:
                print("首次运行，需要设置主密码")
                self.setup_master_password()
            else:
                print("非首次运行，需要登录")
                self.login()

            if self.initialized and self.main_window:
                sys.exit(self.app.exec_())
            else:
                sys.exit(1)

        except Exception as e:
            QMessageBox.critical(None, "错误", f"程序崩溃: {str(e)}")
            print(f"错误详情: {str(e)}")
            sys.exit(1)

    def setup_master_password(self):
        dialog = LoginDialog(mode='setup', crypto=self.storage)
        result = dialog.exec_()  # 获取对话框结果

        print(f"对话框返回结果: {result}")  # 调试输出

        if result == QDialog.Accepted:
            print("对话框已接受，开始处理密码...")
            password = dialog.password_input.text()

            try:
                # 初始化主密钥
                salt = self.storage.initialize_master_key(password)
                print(f"生成的salt: {salt.hex()}")

                # 创建初始数据
                initial_data = {
                    "passwords": [],
                    "categories": [{"id": 1, "name": "默认分类", "parent_id": None}],
                    "master_salt": salt.hex()
                }

                # 保存数据
                self.storage.save_data(initial_data)
                print("数据保存完成，准备显示主窗口...")

                # 显示主窗口
                self.initialized = True
                self.show_main_window()

            except Exception as e:
                print(f"设置密码出错: {str(e)}")
                QMessageBox.critical(None, "错误", f"密码设置失败: {str(e)}")
        else:
            print("对话框被取消")

    def login(self):
        """修正后的登录流程"""
        dialog = LoginDialog(mode='login', crypto=self.storage)
        if dialog.exec_() == QDialog.Accepted:
            password = dialog.password_input.text()

            # 先加载数据获取存储的salt
            data = self.storage.load_data()
            if not data or not data.get("master_salt"):
                QMessageBox.critical(None, "错误", "数据损坏，找不到主密码记录")
                return

            try:
                stored_salt = bytes.fromhex(data["master_salt"])
                # 用存储的salt初始化密钥
                self.storage.initialize_master_key(password, stored_salt)

                if self.storage.verify_password(password):
                    self.initialized = True
                    self.show_main_window()
                else:
                    QMessageBox.warning(None, "错误", "密码不正确")
            except Exception as e:
                QMessageBox.critical(None, "错误", f"验证失败: {str(e)}")

    def show_main_window(self):
        """创建并显示主窗口"""
        try:
            print("正在创建主窗口...")
            self.main_window = MainWindow(self.storage, self.config)
            self.main_window.show()
            print("主窗口显示成功")
        except Exception as e:
            print(f"主窗口创建失败: {str(e)}")
            QMessageBox.critical(None, "错误", f"无法启动主界面: {str(e)}")


if __name__ == "__main__":
    app = PasswordManager()
    app.run()
