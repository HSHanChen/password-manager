"""
@Author: Chan Sheen
@Date: 2025/4/15 17:13
@File: login.py
@Description: 
"""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QMessageBox)


class LoginDialog(QDialog):
    def __init__(self, mode, crypto):
        super().__init__()
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowCloseButtonHint)  # 禁用关闭按钮
        self.mode = mode
        self.crypto = crypto
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("设置主密码" if self.mode == 'setup' else "登录")
        self.setFixedSize(400, 300)

        layout = QVBoxLayout()

        # 密码输入框
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        # 确认密码框（仅设置模式）
        if self.mode == 'setup':
            self.confirm_input = QLineEdit()
            self.confirm_input.setEchoMode(QLineEdit.Password)

            layout.addWidget(QLabel("设置主密码（至少8个字符）:"))
            layout.addWidget(self.password_input)
            layout.addWidget(QLabel("确认密码:"))
            layout.addWidget(self.confirm_input)
        else:
            layout.addWidget(QLabel("请输入主密码:"))
            layout.addWidget(self.password_input)

        # 按钮
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("确定")
        ok_btn.clicked.connect(self.validate)
        btn_layout.addWidget(ok_btn)

        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def validate(self):
        password = self.password_input.text().strip()

        if not password:
            QMessageBox.warning(self, "错误", "密码不能为空")
            return False

        if self.mode == 'setup':
            confirm = self.confirm_input.text().strip()
            if password != confirm:
                QMessageBox.warning(self, "错误", "两次输入的密码不一致")
                return False
            if len(password) < 8:
                QMessageBox.warning(self, "错误", "密码长度至少8个字符")
                return False

        # 必须返回True才会关闭对话框
        return True

    def _on_ok(self):
        if self.validate():  # 只有验证通过才accept
            self.accept()
