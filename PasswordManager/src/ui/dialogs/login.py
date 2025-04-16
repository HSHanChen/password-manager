"""
@Author: Chan Sheen
@Date: 2025/4/15 17:13
@File: login.py
@Description: 
"""

from PyQt5.QtWidgets import (
    QDialog,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QMessageBox,
)


class LoginDialog(QDialog):
    def __init__(self, mode="login", crypto=None, parent=None):
        super().__init__(parent)
        self.mode = mode  # "login" or "setup"
        self.crypto = crypto  # SecureStorage 实例
        self.setWindowTitle("登录" if mode == "login" else "设置主密码")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        self.password_label = QLabel("主密码:" if self.mode == "login" else "请输入主密码:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)

        if self.mode == "setup":
            self.confirm_label = QLabel("请确认主密码:")
            self.confirm_input = QLineEdit()
            self.confirm_input.setEchoMode(QLineEdit.Password)

            layout.addWidget(self.confirm_label)
            layout.addWidget(self.confirm_input)

        # 按钮区域
        button_layout = QHBoxLayout()
        self.confirm_button = QPushButton("确定")
        self.cancel_button = QPushButton("取消")
        button_layout.addWidget(self.confirm_button)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

        # 绑定事件
        self.confirm_button.clicked.connect(self.on_accept)
        self.cancel_button.clicked.connect(self.reject)

    def on_accept(self):
        password = self.password_input.text()
        confirm = self.confirm_input.text() if self.mode == "setup" else None

        if not password:
            QMessageBox.warning(self, "错误", "请输入密码")
            return

        if self.mode == "setup":
            if not confirm:
                QMessageBox.warning(self, "错误", "请确认密码")
                return
            if password != confirm:
                QMessageBox.warning(self, "错误", "两次密码输入不一致")
                return

            # 验证通过，接受对话框
            self.accept()

        elif self.mode == "login":
            if not self.crypto:
                QMessageBox.critical(self, "错误", "未设置加密模块")
                return
            if not self.crypto.verify_password(password):
                QMessageBox.warning(self, "错误", "密码错误")
                return

            # 验证通过
            self.accept()
