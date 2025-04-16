"""
@Author: Chan Sheen
@Date: 2025/4/15 17:13
@File: login.py
@Description:
"""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel,
    QGraphicsDropShadowEffect, QMessageBox
)


# 加载并应用样式表
def load_stylesheet():
    try:
        with open("../resources/qss/main.qss", "r", encoding="utf-8") as style_file:
            return style_file.read()
    except FileNotFoundError:
        # print("样式表文件未找到！")
        return ""  # 如果找不到样式表，返回空样式

class LoginDialog(QDialog):
    def __init__(self, mode, crypto, parent=None):
        super().__init__(parent)

        self.setWindowTitle("设置主密码" if mode == 'setup' else "登录")
        self.setWindowIcon(QIcon("icons/lock_icon.png"))

        self.crypto = crypto
        self.mode = mode

        # 使用加载的样式
        self.setStyleSheet(load_stylesheet())

        # 密码输入框
        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("请输入密码")
        self.password_input.setMinimumWidth(250)  # 设置最小宽度

        # 确认密码输入框
        self.confirm_password_input = QLineEdit(self)
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_input.setPlaceholderText("请确认密码")
        self.confirm_password_input.setMinimumWidth(250)  # 设置最小宽度
        self.confirm_password_input.setVisible(self.mode == 'setup')

        # 眼睛按钮，切换密码可见性
        self.show_eye_button = QPushButton("👁️", self)
        self.show_eye_button.setStyleSheet("background: transparent; border: none; font-size: 18px;")
        self.show_eye_button.clicked.connect(self.toggle_password_visibility)

        # 确认按钮
        self.confirm_button = QPushButton("确定", self)
        self.confirm_button.clicked.connect(self.accept)

        # 取消按钮
        self.cancel_button = QPushButton("取消", self)
        self.cancel_button.setObjectName("cancelButton")  # 给取消按钮设置对象名称
        self.cancel_button.clicked.connect(self.reject)

        # 布局
        layout = QVBoxLayout(self)

        # 标题
        title = QLabel(f"请输入{'设置' if mode == 'setup' else '登录'}密码", self)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 提示文字
        tip = QLabel("由于您是首次登录，请设置主密码" if mode == 'setup' else "", self)
        tip.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(tip)
        layout.addWidget(title)

        # 密码输入框和眼睛按钮布局
        pass_layout = QHBoxLayout()
        pass_layout.addWidget(self.password_input)
        pass_layout.addWidget(self.show_eye_button)

        layout.addLayout(pass_layout)

        # 如果是首次设置密码，添加确认密码输入框
        if self.mode == 'setup':
            confirm_layout = QHBoxLayout()
            confirm_layout.addWidget(self.confirm_password_input)
            confirm_layout.addWidget(self.show_eye_button)

            layout.addLayout(confirm_layout)

        # 按钮布局
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
