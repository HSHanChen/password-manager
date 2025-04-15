"""
@Author: Henve
@Date: 2025/4/15 14:33
@File: password_model.py
@Description: 
"""
from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex


class PasswordTableModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.headers = ["ID", "分类", "名称", "网址", "账号", "密码", "备注"]
        self.column_keys = ["id", "category_name", "name", "url", "username", "password", "notes"]

    def rowCount(self, parent=QModelIndex()):
        return len(self.data)

    def columnCount(self, parent=QModelIndex()):
        return len(self.headers)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.headers[section]
        return None

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        row = index.row()
        col = index.column()

        if role == Qt.DisplayRole:
            key = self.column_keys[col]
            value = self.data[row].get(key, "")

            if key == "password":
                return "******"  # 密码显示为星号
            return str(value) if value is not None else ""

        return None

    def get_entry(self, row):
        if 0 <= row < len(self.data):
            return self.data[row]
        return None