"""
@Author: Chan Sheen
@Date: 2025/4/15 16:20
@File: main.py
@Description: 
"""
import sys
from PyQt5.QtWidgets import QApplication, QMessageBox
from config import AppConfig
from secure_storage import SecureStorage
from styles import get_stylesheet
from ui.main_window import MainWindow
from ui.login_dialog import LoginDialog


class PasswordManagerApp:
    def __init__(self):
        self.config = AppConfig()
        self.storage = SecureStorage(self.config)
        self.app = QApplication(sys.argv)
        self.app.setStyle('Fusion')
        self.app.setStyleSheet(get_stylesheet())

    def run(self):
        if self.is_first_run():
            self.setup_master_password()
        else:
            self.login()

        sys.exit(self.app.exec_())

    def is_first_run(self):
        data = self.storage.load_data()
        return data["master_salt"] is None

    def setup_master_password(self):
        dialog = LoginDialog(mode='setup', crypto=self.storage)
        if dialog.exec_():
            data = {
                "passwords": [],
                "categories": [{"id": 1, "name": "默认分类", "parent_id": None}],
                "master_salt": self.storage.salt.hex()
            }
            self.storage.save_data(data)
            self.show_main_window()

    def login(self):
        dialog = LoginDialog(mode='login', crypto=self.storage)
        if dialog.exec_():
            self.show_main_window()

    def show_main_window(self):
        window = MainWindow(self.storage, self.config)
        window.show()


if __name__ == "__main__":
    manager = PasswordManagerApp()
    manager.run()