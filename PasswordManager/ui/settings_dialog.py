"""
@Author: Chan Sheen
@Date: 2025/4/15 16:22
@File: settings_dialog.py
@Description: 
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QFileDialog)


class SettingsDialog(QDialog):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.setWindowTitle("设置")
        self.setFixedSize(500, 200)

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout()

        # 数据文件路径设置
        path_layout = QHBoxLayout()
        path_label = QLabel("数据文件位置:")
        self.path_input = QLineEdit()
        self.path_input.setText(str(self.config.data_path))
        path_button = QPushButton("浏览...")
        path_button.clicked.connect(self._select_path)

        path_layout.addWidget(path_label)
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(path_button)

        # 按钮
        button_layout = QHBoxLayout()
        save_button = QPushButton("保存")
        save_button.clicked.connect(self._save_settings)
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)

        layout.addLayout(path_layout)
        layout.addStretch()
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _select_path(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "选择数据文件",
            str(self.config.data_path),
            "Data Files (*.dat)"
        )
        if path:
            self.path_input.setText(path)

    def _save_settings(self):
        new_path = self.path_input.text().strip()
        if new_path and new_path != str(self.config.data_path):
            # 移动现有数据文件
            try:
                import shutil
                if self.config.data_path.exists():
                    shutil.move(str(self.config.data_path), new_path)
                self.config.save_config(new_path)
            except Exception as e:
                QMessageBox.warning(self, "错误", f"无法移动数据文件: {str(e)}")
                return

        self.accept()