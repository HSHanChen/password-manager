"""
@Author: Chan Sheen
@Date: 2025/4/15 17:13
@File: settings.py
@Description: 
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QFileDialog, QMessageBox)


class SettingsDialog(QDialog):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.setWindowTitle("数据文件设置")
        self.setFixedSize(500, 200)

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout()

        # 当前路径显示
        current_path_label = QLabel("当前数据文件位置:")
        self.current_path_display = QLineEdit()
        self.current_path_display.setText(str(self.config.data_path))
        self.current_path_display.setReadOnly(True)

        # 新路径设置
        new_path_label = QLabel("新数据文件位置:")
        self.new_path_input = QLineEdit()
        browse_button = QPushButton("浏览...")
        browse_button.clicked.connect(self._browse_path)

        path_layout = QHBoxLayout()
        path_layout.addWidget(self.new_path_input)
        path_layout.addWidget(browse_button)

        # 按钮布局
        button_layout = QHBoxLayout()
        save_button = QPushButton("保存")
        save_button.clicked.connect(self._save_settings)
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)

        # 组装布局
        layout.addWidget(current_path_label)
        layout.addWidget(self.current_path_display)
        layout.addWidget(new_path_label)
        layout.addLayout(path_layout)
        layout.addStretch()
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _browse_path(self):
        """选择新数据文件路径"""
        path, _ = QFileDialog.getSaveFileName(
            self, "选择数据文件位置",
            str(self.config.data_path.parent),
            "Data Files (*.dat)"
        )
        if path:
            self.new_path_input.setText(path)

    def _save_settings(self):
        """保存新设置"""
        new_path = self.new_path_input.text().strip()
        if not new_path:
            QMessageBox.warning(self, "错误", "请输入有效路径")
            return

        try:
            import shutil
            # 如果新旧路径不同且旧文件存在，则移动文件
            if (new_path != str(self.config.data_path) and
                    self.config.data_path.exists()):
                shutil.move(str(self.config.data_path), new_path)

            # 更新配置
            self.config.save_config(new_path)
            QMessageBox.information(self, "成功", "设置已保存，重启后生效")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存失败: {str(e)}")
