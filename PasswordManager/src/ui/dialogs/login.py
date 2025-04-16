"""
@Author: Chan Sheen
@Date: 2025/4/15 17:13
@File: login.py
@Description: 
"""

from PyQt6.QtCore import Qt, QFile, QTextStream
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel,
    QGraphicsDropShadowEffect, QMessageBox
)


def load_stylesheet():
    style_file = QFile(":/qss/main.qss")
    if style_file.open(QFile.ReadOnly | QFile.Text):
        stream = QTextStream(style_file)
        return stream.readAll()
    return """
    QMainWindow {
        background-color: #f5f5f5;
    }
    QStatusBar {
        background: #e0e7ff;
    }
    """


class LoginDialog(QDialog):
    def __init__(self, mode, crypto, parent=None):
        super().__init__(parent)

        self.setWindowTitle("设置主密码" if mode == 'setup' else "登录")
        self.setWindowIcon(QIcon("icons/lock_icon.png"))

        self.crypto = crypto
        self.mode = mode

        # 使用加载的样式
        self.setStyleSheet(load_stylesheet())

        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("请输入密码")
        self.password_input.setStyleSheet(
            "padding: 10px; font-size: 14px; border-radius: 8px; border: 1px solid #cccccc; background-color: #ffffff;")

        self.confirm_password_input = QLineEdit(self)
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_input.setPlaceholderText("请确认密码")
        self.confirm_password_input.setStyleSheet(
            "padding: 10px; font-size: 14px; border-radius: 8px; border: 1px solid #cccccc; background-color: #ffffff;")
        self.confirm_password_input.setVisible(self.mode == 'setup')

        self.show_eye_button = QPushButton("👁️", self)
        self.show_eye_button.setStyleSheet("background: transparent; border: none; font-size: 18px;")
        self.show_eye_button.clicked.connect(self.toggle_password_visibility)

        self.confirm_button = QPushButton("确定", self)
        self.confirm_button.clicked.connect(self.accept)

        self.cancel_button = QPushButton("取消", self)
        self.cancel_button.clicked.connect(self.reject)

        layout = QVBoxLayout(self)

        title = QLabel(f"请输入{'设置' if mode == 'setup' else '登录'}密码", self)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        tip = QLabel("由于您是首次登录，请设置主密码" if mode == 'setup' else "", self)
        tip.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(title)
        layout.addWidget(tip)

        pass_layout = QHBoxLayout()
        pass_layout.addWidget(self.password_input)
        pass_layout.addWidget(self.show_eye_button)

        layout.addLayout(pass_layout)

        if self.mode == 'setup':
            layout.addWidget(self.confirm_password_input)

        btns = QHBoxLayout()
        btns.addWidget(self.cancel_button)
        btns.addWidget(self.confirm_button)

        layout.addLayout(btns)
        self.setFixedSize(400, 300)

        # 设置阴影效果
        self.setGraphicsEffect(self.create_shadow_effect())  # 使用阴影效果

    def toggle_password_visibility(self):
        if self.password_input.echoMode() == QLineEdit.EchoMode.Password:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)

    def create_shadow_effect(self):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setOffset(0, 0)
        shadow.setColor(Qt.GlobalColor.gray)
        return shadow

    def accept(self):
        password = self.password_input.text()
        confirm = self.confirm_password_input.text()

        if not password:
            QMessageBox.warning(self, "错误", "密码不能为空")
            return

        if self.mode == 'setup' and password != confirm:
            QMessageBox.warning(self, "错误", "两次输入的密码不一致")
            return

        super().accept()
