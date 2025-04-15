"""
@Author: Henve
@Date: 2025/4/15 14:32
@File: login_dialog.py
@Description: 
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                            QLineEdit, QPushButton, QMessageBox)
from PyQt5.QtCore import Qt


class LoginDialog(QDialog):
    def __init__(self, mode, crypto):
        super().__init__()
        self.mode = mode
        self.crypto = crypto

        self.setWindowTitle("密码管理器")
        self.setFixedSize(300, 200)

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout()

        if self.mode == 'setup':
            title = "设置主密码"
            instruction = "这是您第一次使用密码管理器，请设置一个主密码。\n请牢记此密码，它将用于加密您的所有密码。"
        elif self.mode == 'login':
            title = "输入主密码"
            instruction = "请输入您的主密码以解锁密码管理器。"
        else:  # change
            title = "修改主密码"
            instruction = "请输入当前主密码和新主密码。"

        self.setWindowTitle(title)

        # 说明标签
        self.instruction_label = QLabel(instruction)
        self.instruction_label.setWordWrap(True)
        layout.addWidget(self.instruction_label)

        # 当前密码输入框 (修改密码时显示)
        if self.mode == 'change':
            self.current_password_label = QLabel("当前密码:")
            self.current_password_input = QLineEdit()
            self.current_password_input.setEchoMode(QLineEdit.Password)
            layout.addWidget(self.current_password_label)
            layout.addWidget(self.current_password_input)

        # 新密码输入框 (设置/修改密码时显示)
        if self.mode in ['setup', 'change']:
            self.new_password_label = QLabel("新密码:" if self.mode == 'change' else "主密码:")
            self.new_password_input = QLineEdit()
            self.new_password_input.setEchoMode(QLineEdit.Password)
            layout.addWidget(self.new_password_label)
            layout.addWidget(self.new_password_input)

            self.confirm_password_label = QLabel("确认密码:")
            self.confirm_password_input = QLineEdit()
            self.confirm_password_input.setEchoMode(QLineEdit.Password)
            layout.addWidget(self.confirm_password_label)
            layout.addWidget(self.confirm_password_input)
        else:  # login
            self.password_label = QLabel("主密码:")
            self.password_input = QLineEdit()
            self.password_input.setEchoMode(QLineEdit.Password)
            layout.addWidget(self.password_label)
            layout.addWidget(self.password_input)

        # 按钮
        self.ok_button = QPushButton("确定")
        self.ok_button.clicked.connect(self._on_ok)
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _on_ok(self):
        if self.mode == 'setup':
            self._handle_setup()
        elif self.mode == 'login':
            self._handle_login()
        else:  # change
            self._handle_change()

    def _handle_setup(self):
        password = self.new_password_input.text()
        confirm = self.confirm_password_input.text()

        if not password:
            QMessageBox.warning(self, "错误", "密码不能为空")
            return

        if password != confirm:
            QMessageBox.warning(self, "错误", "两次输入的密码不一致")
            return

        if len(password) < 8:
            QMessageBox.warning(self, "错误", "密码长度至少为8个字符")
            return

        # 设置主密码
        salt = self.crypto.set_master_key(password)
        hashed_key = self.crypto.hash_for_storage(self.crypto.master_key)

        # 存储到数据库
        from database import Database
        db = Database()
        db.set_master_password(salt, hashed_key)
        db.close()

        self.accept()

    def _handle_login(self):
        password = self.password_input.text()

        if not password:
            QMessageBox.warning(self, "错误", "密码不能为空")
            return

        # 从数据库获取存储的salt和hash
        from database import Database
        db = Database()
        stored_data = db.get_master_password()
        db.close()

        if not stored_data:
            QMessageBox.critical(self, "错误", "找不到主密码记录")
            return

        salt, stored_hash = stored_data

        # 验证密码
        if self.crypto.verify_master_password(password, salt, stored_hash):
            # 设置当前会话的主密钥
            self.crypto.set_master_key(password, salt)
            self.accept()
        else:
            QMessageBox.warning(self, "错误", "密码不正确")

    def _handle_change(self):
        current_password = self.current_password_input.text()
        new_password = self.new_password_input.text()
        confirm_password = self.confirm_password_input.text()

        if not current_password or not new_password or not confirm_password:
            QMessageBox.warning(self, "错误", "所有字段都必须填写")
            return

        if new_password != confirm_password:
            QMessageBox.warning(self, "错误", "新密码和确认密码不匹配")
            return

        if len(new_password) < 8:
            QMessageBox.warning(self, "错误", "新密码长度至少为8个字符")
            return

        # 验证当前密码
        from database import Database
        db = Database()
        stored_data = db.get_master_password()

        if not stored_data:
            QMessageBox.critical(self, "错误", "找不到主密码记录")
            db.close()
            return

        salt, stored_hash = stored_data

        if not self.crypto.verify_master_password(current_password, salt, stored_hash):
            QMessageBox.warning(self, "错误", "当前密码不正确")
            db.close()
            return

        # 设置新密码
        new_salt = self.crypto.set_master_key(new_password)
        new_hashed_key = self.crypto.hash_for_storage(self.crypto.master_key)

        # 更新数据库
        db.set_master_password(new_salt, new_hashed_key)

        # 重新加密所有密码
        entries = db.get_password_entries()

        for entry in entries:
            try:
                # 使用旧密钥解密
                old_key = PBKDF2(
                    current_password.encode('utf-8'),
                    salt,
                    dkLen=32,
                    count=100000
                )
                self.crypto.master_key = old_key
                plaintext = self.crypto.decrypt_password(entry['encrypted_password'])

                # 使用新密钥加密
                self.crypto.master_key = new_hashed_key
                encrypted_password = self.crypto.encrypt_password(plaintext)

                # 更新数据库
                db.update_password_entry(entry['id'], {
                    'category_id': entry['category_id'],
                    'name': entry['name'],
                    'url': entry['url'],
                    'username': entry['username'],
                    'encrypted_password': encrypted_password,
                    'notes': entry['notes']
                })

            except Exception as e:
                QMessageBox.critical(self, "错误", f"密码迁移失败: {str(e)}")
                db.close()
                return

        db.close()
        self.accept()