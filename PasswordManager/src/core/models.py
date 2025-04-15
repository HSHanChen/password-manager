"""
@Author: Chan Sheen
@Date: 2025/4/15 17:11
@File: models.py
@Description: 
"""
from PyQt5.QtCore import Qt, QAbstractTableModel


class PasswordTableModel(QAbstractTableModel):
    def __init__(self, passwords, categories):
        super().__init__()
        self.passwords = passwords
        self.categories = {c['id']: c['name'] for c in categories}
        self.headers = ["名称", "分类", "账号", "网址", "备注"]

    def rowCount(self, parent=None):
        return len(self.passwords)

    def columnCount(self, parent=None):
        return len(self.headers)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        row, col = index.row(), index.column()
        item = self.passwords[row]

        if role == Qt.DisplayRole:
            return {
                0: item.get('name', ''),
                1: self.categories.get(item.get('category_id'), '无分类'),
                2: item.get('username', ''),
                3: item.get('url', ''),
                4: item.get('notes', '')
            }.get(col, '')
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.headers[section]
        return None
