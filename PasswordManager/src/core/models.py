"""
@Author: Chan Sheen
@Date: 2025/4/15 17:11
@File: models.py
@Description: 
"""

from PyQt6.QtCore import Qt, QAbstractTableModel, QModelIndex
from PyQt6.QtGui import QStandardItemModel, QStandardItem


class PasswordTableModel(QAbstractTableModel):
    def __init__(self, passwords, categories):
        super().__init__()
        self.passwords = passwords
        self.categories = {c['id']: c['name'] for c in categories}
        self.headers = ["名称", "分类", "账号", "网址", "备注"]

    def rowCount(self, parent=QModelIndex()):
        return len(self.passwords)

    def columnCount(self, parent=QModelIndex()):
        return len(self.headers)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        row = index.row()
        col = index.column()
        item = self.passwords[row]

        if role == Qt.ItemDataRole.DisplayRole:
            return {
                0: item.get('name', ''),
                1: self.categories.get(item.get('category_id'), '无分类'),
                2: item.get('username', ''),
                3: item.get('url', ''),
                4: item.get('notes', '')
            }.get(col, '')
        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.ItemDataRole.Horizontal:
            return self.headers[section]
        return None


class CategoryTreeModel(QStandardItemModel):
    def __init__(self, categories):
        super().__init__()
        self.setHorizontalHeaderLabels(["分类"])
        self.categories = categories
        self._setup_model()

    def _setup_model(self):
        self.clear()

        # 创建所有分类项
        items = {}
        for cat in self.categories:
            item = QStandardItem(cat['name'])
            item.setData(cat['id'], Qt.UserRole)
            items[cat['id']] = item

        # 构建树结构
        for cat in self.categories:
            parent_id = cat['parent_id']
            item = items[cat['id']]

            if parent_id is None:
                self.appendRow(item)
            elif parent_id in items:
                items[parent_id].appendRow(item)
            else:
                self.appendRow(item)
