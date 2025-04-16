"""
@Author: Chan Sheen
@Date: 2025/4/15 17:13
@File: password.py
@Description: 
"""
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLineEdit, QComboBox, QPushButton)


class PasswordDialog(QDialog):
    def __init__(self, mode, categories, entry_data=None):
        super().__init__()
        self.mode = mode
        self.categories = categories
        self.entry_data = entry_data or {}
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("添加密码" if self.mode == 'add' else "编辑密码")
        self.setFixedSize(500, 400)

        layout = QVBoxLayout()
        form = QFormLayout()

        # 名称
        self.name_input = QLineEdit()
        form.addRow("名称:", self.name_input)

        # 分类
        self.category_combo = QComboBox()
        self.category_combo.addItem("无分类", None)
        for cat in self.categories:
            self.category_combo.addItem(cat['name'], cat['id'])
        form.addRow("分类:", self.category_combo)

        # 网址
        self.url_input = QLineEdit()
        form.addRow("网址:", self.url_input)

        # 用户名
        self.username_input = QLineEdit()
        form.addRow("用户名:", self.username_input)

        # 密码
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.toggle_btn = QPushButton()
        self.toggle_btn.setIcon(QIcon(":/icons/eye.svg"))
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.clicked.connect(self.toggle_password)

        pass_layout = QHBoxLayout()
        pass_layout.addWidget(self.password_input)
        pass_layout.addWidget(self.toggle_btn)
        form.addRow("密码:", pass_layout)

        # 备注
        self.notes_input = QLineEdit()
        form.addRow("备注:", self.notes_input)

        layout.addLayout(form)

        # 按钮
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("确定")
        ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(ok_btn)

        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)

        # 填充现有数据
        if self.entry_data:
            self.name_input.setText(self.entry_data.get('name', ''))
            self.url_input.setText(self.entry_data.get('url', ''))
            self.username_input.setText(self.entry_data.get('username', ''))
            self.password_input.setText(self.entry_data.get('password', ''))
            self.notes_input.setText(self.entry_data.get('notes', ''))

            # 设置分类
            cat_id = self.entry_data.get('category_id')
            index = self.category_combo.findData(cat_id)
            if index >= 0:
                self.category_combo.setCurrentIndex(index)

        self.setLayout(layout)

    def toggle_password(self):
        """切换密码可见性"""
        if self.toggle_btn.isChecked():
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.toggle_btn.setIcon(QIcon(":/icons/eye_closed.svg"))
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.toggle_btn.setIcon(QIcon(":/icons/eye.svg"))

    def get_entry_data(self):
        """获取表单数据"""
        return {
            'name': self.name_input.text().strip(),
            'url': self.url_input.text().strip(),
            'username': self.username_input.text().strip(),
            'password': self.password_input.text(),
            'notes': self.notes_input.text().strip(),
            'category_id': self.category_combo.currentData()
        }
