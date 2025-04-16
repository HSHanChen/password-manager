"""
@Author: Chan Sheen
@Date: 2025/4/15 17:13
@File: login.py
@Description: 
"""

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, QGraphicsDropShadowEffect


class LoginDialog(QDialog):
    def __init__(self, mode, crypto, parent=None):
        super().__init__(parent)

        self.setWindowTitle("设置主密码" if mode == 'setup' else "登录")
        self.setWindowIcon(QIcon("icons/lock_icon.png"))  # 可自定义图标

        self.crypto = crypto
        self.mode = mode

        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)  # 默认密码框
        self.password_input.setPlaceholderText("请输入密码")  # 提示文本
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                font-size: 14px;
                border-radius: 15px;
                border: 1px solid #ccc;
                background-color: #ffffff;
            }
        """)

        self.confirm_password_input = QLineEdit(self)
        self.confirm_password_input.setEchoMode(QLineEdit.Password)  # 默认密码框
        self.confirm_password_input.setPlaceholderText("请确认密码")  # 提示文本
        self.confirm_password_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                font-size: 14px;
                border-radius: 15px;
                border: 1px solid #ccc;
                background-color: #ffffff;
            }
        """)

        self.show_eye_button = QPushButton("👁️", self)
        self.show_eye_button.setStyleSheet("background: transparent; border: none; font-size: 18px;")
        self.show_eye_button.clicked.connect(self.toggle_password_visibility)

        self.confirm_button = QPushButton("确定", self)
        self.confirm_button.setStyleSheet("""
            QPushButton {
                padding: 12px;
                background-color: #4CAF50;
                color: white;
                border-radius: 10px;
                font-size: 16px;
                border: none;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.confirm_button.clicked.connect(self.accept)

        self.cancel_button = QPushButton("取消", self)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                padding: 12px;
                background-color: #f44336;
                color: white;
                border-radius: 10px;
                font-size: 16px;
                border: none;
            }
            QPushButton:hover {
                background-color: #e53935;
            }
        """)
        self.cancel_button.clicked.connect(self.reject)

        self.layout = QVBoxLayout(self)

        # 创建顶部标题
        self.title_label = QLabel(f"请输入{'设置' if mode == 'setup' else '登录'}密码", self)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #333;
                margin-bottom: 10px;
            }
        """)

        # 提示文字
        self.tip_label = QLabel("由于您是首次登录，请设置主密码", self)
        self.tip_label.setAlignment(Qt.AlignCenter)
        self.tip_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #666;
                margin-bottom: 20px;
            }
        """)

        # 密码行
        self.password_layout = QVBoxLayout()
        self.password_layout.addWidget(self.password_input)
        self.password_layout.addWidget(self.confirm_password_input)

        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.tip_label)  # 添加提示文字
        self.layout.addLayout(self.password_layout)

        # 添加按钮
        self.button_layout = QHBoxLayout()
        self.button_layout.addWidget(self.cancel_button)
        self.button_layout.addWidget(self.confirm_button)
        self.layout.addLayout(self.button_layout)

        self.layout.setContentsMargins(30, 30, 30, 30)
        self.layout.setSpacing(15)

        # 设置背景色
        self.setStyleSheet("QDialog { background-color: #f4f4f4; }")

        self.setFixedSize(400, 300)
        self.setShadowEffect()

    def toggle_password_visibility(self):
        """
        切换密码输入框的显示/隐藏状态
        """
        if self.password_input.echoMode() == QLineEdit.Password:
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.confirm_password_input.setEchoMode(QLineEdit.Normal)  # 显示确认密码框的内容
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.confirm_password_input.setEchoMode(QLineEdit.Password)  # 隐藏确认密码框的内容

    def setShadowEffect(self):
        """
        设置对话框的阴影效果
        """
        shadow_effect = QGraphicsDropShadowEffect()
        shadow_effect.setBlurRadius(10)
        shadow_effect.setOffset(0, 0)
        shadow_effect.setColor(Qt.black)
        self.setGraphicsEffect(shadow_effect)

    def accept(self):
        """
        确认按钮点击事件，进行密码一致性验证
        """
        if self.password_input.text() != self.confirm_password_input.text():
            QMessageBox.warning(self, "错误", "两次输入的密码不一致，请重新输入。")
            return
        super().accept()
