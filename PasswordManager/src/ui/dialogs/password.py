"""
@Author: Chan Sheen
@Date: 2025/4/15 17:13
@File: password.py
@Description:
"""

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit,
    QComboBox, QPushButton, QMessageBox
)


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
        self.setModal(True)

        # 设置背景颜色
        # self.setStyleSheet("background-color: #f5f5f5;")

        layout = QVBoxLayout()
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form.setHorizontalSpacing(20)
        form.setVerticalSpacing(12)

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
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        # self.password_input.setStyleSheet("background-color: white; padding-right: 30px;")  # 输入框背景色与间距

        # 眼睛图标按钮
        self.toggle_btn = QPushButton()
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.setFlat(True)
        self.toggle_btn.setFixedSize(28, 28)
        self.toggle_btn.setIcon(QIcon(":/icons/eye.svg"))
        self.toggle_btn.setIconSize(QSize(20, 20))
        self.toggle_btn.clicked.connect(self.toggle_password)

        # 布局调整：密码框和眼睛按钮在同一行
        pass_layout = QHBoxLayout()
        pass_layout.setContentsMargins(0, 0, 0, 0)  # 去掉布局边距
        pass_layout.addWidget(self.password_input)
        pass_layout.addWidget(self.toggle_btn)
        form.addRow("密码:", pass_layout)

        # 备注
        self.notes_input = QLineEdit()
        form.addRow("备注:", self.notes_input)

        layout.addLayout(form)

        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch(1)

        ok_btn = QPushButton("确定")
        ok_btn.setFixedWidth(80)
        ok_btn.clicked.connect(self.validate_and_accept)
        btn_layout.addWidget(ok_btn)

        cancel_btn = QPushButton("取消")
        cancel_btn.setFixedWidth(80)
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
            index = self.category_combo.findData(self.entry_data.get('category_id'))
            if index >= 0:
                self.category_combo.setCurrentIndex(index)

        self.setLayout(layout)

        # 默认聚焦到名称输入框
        self.name_input.setFocus()
        self.name_input.returnPressed.connect(ok_btn.click)
        self.password_input.returnPressed.connect(ok_btn.click)

    def toggle_password(self):
        if self.toggle_btn.isChecked():
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.toggle_btn.setIcon(QIcon(":/icons/eye_closed.svg"))
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.toggle_btn.setIcon(QIcon(":/icons/eye.svg"))

    def validate_and_accept(self):
        """检查表单合法性"""
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "提示", "名称不能为空")
            self.name_input.setFocus()
            return
        if not self.password_input.text():
            QMessageBox.warning(self, "提示", "密码不能为空")
            self.password_input.setFocus()
            return
        self.accept()

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
