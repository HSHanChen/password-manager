"""
@Author: Henve
@Date: 2025/4/15 14:33
@File: category_model.py
@Description: 
"""
from PyQt5.QtCore import Qt, QAbstractItemModel, QModelIndex
from PyQt5.QtGui import QStandardItem


class CategoryTreeModel(QAbstractItemModel):
    def __init__(self, categories):
        super().__init__()
        self.root_item = QStandardItem()
        self.root_item.setData("分类", Qt.DisplayRole)
        self._setup_model_data(categories)

    def _setup_model_data(self, categories):
        # 创建所有分类项
        items = {}
        for cat in categories:
            item = QStandardItem()
            item.setData(cat['name'], Qt.DisplayRole)
            item.setData(cat['id'], Qt.UserRole)
            items[cat['id']] = item

        # 构建树结构
        for cat in categories:
            parent_id = cat['parent_id']
            item = items[cat['id']]

            if parent_id is None:
                self.root_item.appendRow(item)
            else:
                if parent_id in items:
                    items[parent_id].appendRow(item)
                else:
                    self.root_item.appendRow(item)

    def index(self, row, column, parent=QModelIndex()):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            parent_item = self.root_item
        else:
            parent_item = parent.internalPointer()

        child_item = parent_item.child(row, column)
        if child_item:
            return self.createIndex(row, column, child_item)
        return QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()

        child_item = index.internalPointer()
        parent_item = child_item.parent()

        if parent_item == self.root_item or not parent_item:
            return QModelIndex()

        return self.createIndex(parent_item.row(), 0, parent_item)

    def rowCount(self, parent=QModelIndex()):
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parent_item = self.root_item
        else:
            parent_item = parent.internalPointer()

        return parent_item.rowCount()

    def columnCount(self, parent=QModelIndex()):
        return 1

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        item = index.internalPointer()

        if role == Qt.DisplayRole:
            return item.data(role)
        elif role == Qt.UserRole:
            return item.data(role)

        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.root_item.data(role)
        return None