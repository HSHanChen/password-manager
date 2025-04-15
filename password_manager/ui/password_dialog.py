"""
@Author: Henve
@Date: 2025/4/15 14:39
@File: password_dialog.py
@Description: 
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                            QLineEdit, QComboBox, QPushButton, QLabel)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from ui.resources import *


class PasswordDialog(QDialog):
    def __init__(self, mode, categories, entry_data=None):
        super().__init__()
        self.mode = mode
        self.categories = categories
        self.entry_data = entry_data or {}

        self.setWindowTitle("添加密码" if mode == 'add' else "编辑密码")
        self.setFixedSize(400, 300)

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout()

        # 表单布局
        form_layout = QFormLayout()

        # 分类
        self.category_combo = QComboBox()
        self._populate_categories()
        form_layout.addRow("分类:", self.category_combo)

        # 名称
        self.name_input = QLineEdit()
        form_layout.addRow("名称:", self.name_input)

        # 网址
        self.url_input = QLineEdit()
        form_layout.addRow("网址:", self.url_input)

        # 账号
        self.username_input = QLineEdit()
        form_layout.addRow("账号:", self.username_input)

        # 密码
        password_layout = QHBoxLayout()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        password_layout.addWidget(self.password_input)

        self.toggle_password_button = QPushButton()
        self.toggle_password_button.setIcon(QIcon(":/eye.svg"))
        self.toggle_password_button.setCheckable(True)
        self.toggle_password_button.clicked.connect(self._toggle_password_visibility)
        password_layout.addWidget(self.toggle_password_button)

        form_layout.addRow("密码:", password_layout)

        # 备注
        self.notes_input = QLineEdit()
        form_layout.addRow("备注:", self.notes_input)

        layout.addLayout(form_layout)

        # 按钮
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("确定")
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        # 如果是编辑模式，填充数据
        if self.mode == 'edit' and self.entry_data:
            self._fill_form_data()

    def _populate_categories(self):
        # 添加顶级分类
        self.category_combo.addItem("无分类", None)

        # 添加其他分类
        for cat in self.categories:
            if cat['parent_id'] is None:  # 只添加顶级分类
                self.category_combo.addItem(cat['name'], cat['id'])

        # 设置当前选中的分类
        if 'category_id' in self.entry_data:
            index = self.category_combo.findData(self.entry_data['category_id'])
            if index >= 0:
                self.category_combo.setCurrentIndex(index)

    def _fill_form_data(self):
        self.name_input.setText(self.entry_data.get('name', ''))
        self.url_input.setText(self.entry_data.get('url', ''))
        self.username_input.setText(self.entry_data.get('username', ''))
        self.password_input.setText(self.entry_data.get('password', ''))
        self.notes_input.setText(self.entry_data.get('notes', ''))

    def _toggle_password_visibility(self):
        if self.toggle_password_button.isChecked():
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.toggle_password_button.setIcon(QIcon(":/resources/eye_closed.svg"))
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.toggle_password_button.setIcon(QIcon(":/resources/eye.svg"))

    def get_entry_data(self):
        return {
            'category_id': self.category_combo.currentData(),
            'name': self.name_input.text().strip(),
            'url': self.url_input.text().strip(),
            'username': self.username_input.text().strip(),
            'password': self.password_input.text(),
            'notes': self.notes_input.text().strip()
        }