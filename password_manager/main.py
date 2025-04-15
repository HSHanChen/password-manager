"""
@Author: Henve
@Date: 2025/4/15 14:31
@File: database.py
@Description:
"""

import sys
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow
from database import Database
from utils.crypto import CryptoUtils

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 初始化数据库和加密
    db = Database()
    crypto = CryptoUtils()

    # 检查是否是首次运行
    if db.is_first_run():
        from ui.login_dialog import LoginDialog

        dialog = LoginDialog(mode='setup', crypto=crypto)
        if dialog.exec_() == LoginDialog.Accepted:
            window = MainWindow(db, crypto)
            window.show()
        else:
            sys.exit(0)
    else:
        from ui.login_dialog import LoginDialog

        dialog = LoginDialog(mode='login', crypto=crypto)
        if dialog.exec_() == LoginDialog.Accepted:
            window = MainWindow(db, crypto)
            window.show()
        else:
            sys.exit(0)

    sys.exit(app.exec_())