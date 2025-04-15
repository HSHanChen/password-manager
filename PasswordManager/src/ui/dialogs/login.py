"""
@Author: Chan Sheen
@Date: 2025/4/15 17:13
@File: login.py
@Description: 
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit,
                             QPushButton)


class LoginDialog(QDialog):
    def __init__(self, mode, crypto):
        super().__init__()
        self.mode = mode
        self.crypto = crypto
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("登录" if self.mode == 'login' else "设置密码")
        self.setFixedSize(400, 300)

        layout = QVBoxLayout()

        # 密码输入
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        if self.mode == 'setup':
            self.confirm_input = QLineEdit()
            self.confirm_input.setEchoMode(QLineEdit.Password)
            layout.addWidget(QLabel("设置主密码:"))
            layout.addWidget(self.password_input)
            layout.addWidget(QLabel("确认密码:"))
            layout.addWidget(self.confirm_input)
        else:
            layout.addWidget(QLabel("输入主密码:"))
            layout.addWidget(self.password_input)

        # 按钮
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("确定")
        ok_btn.clicked.connect(self.verify)
        btn_layout.addWidget(ok_btn)

        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def verify(self):
        # 验证逻辑
        self.accept()
