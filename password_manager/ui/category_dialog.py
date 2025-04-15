"""
@Author: Henve
@Date: 2025/4/15 14:53
@File: category_dialog.py
@Description: 
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTreeWidget,
                             QTreeWidgetItem, QPushButton, QLineEdit, QInputDialog)


class CategoryDialog(QDialog):
    def __init__(self, categories):
        super().__init__()
        self.categories = categories
        self.setWindowTitle("管理分类")
        self.setFixedSize(400, 500)

        self._setup_ui()
        self._load_categories()

    def _setup_ui(self):
        layout = QVBoxLayout()

        # 分类树
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("分类")
        layout.addWidget(self.tree)

        # 操作按钮
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("添加")
        self.add_button.clicked.connect(self._on_add)
        self.edit_button = QPushButton("编辑")
        self.edit_button.clicked.connect(self._on_edit)
        self.delete_button = QPushButton("删除")
        self.delete_button.clicked.connect(self._on_delete)

        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        layout.addLayout(button_layout)

        # 确定/取消按钮
        bottom_layout = QHBoxLayout()
        self.ok_button = QPushButton("确定")
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)

        bottom_layout.addStretch()
        bottom_layout.addWidget(self.ok_button)
        bottom_layout.addWidget(self.cancel_button)
        layout.addLayout(bottom_layout)

        self.setLayout(layout)

    def _load_categories(self):
        self.tree.clear()

        # 创建顶级分类项
        top_level_items = {}
        for cat in self.categories:
            if cat['parent_id'] is None:
                item = QTreeWidgetItem(self.tree)
                item.setText(0, cat['name'])
                item.setData(0, Qt.UserRole, cat['id'])
                top_level_items[cat['id']] = item

        # 添加子分类
        for cat in self.categories:
            if cat['parent_id'] is not None and cat['parent_id'] in top_level_items:
                parent_item = top_level_items[cat['parent_id']]
                item = QTreeWidgetItem(parent_item)
                item.setText(0, cat['name'])
                item.setData(0, Qt.UserRole, cat['id'])

    def _on_add(self):
        selected = self.tree.selectedItems()
        parent_id = None

        if selected:
            parent_item = selected[0]
            parent_id = parent_item.data(0, Qt.UserRole)

        name, ok = QInputDialog.getText(self, "添加分类", "请输入分类名称:")
        if ok and name:
            from database import Database
            db = Database()
            db.add_category(name, parent_id)
            db.close()

            # 刷新列表
            self.categories = db.get_categories()
            self._load_categories()

    def _on_edit(self):
        selected = self.tree.selectedItems()
        if not selected:
            return

        item = selected[0]
        old_name = item.text(0)
        cat_id = item.data(0, Qt.UserRole)

        name, ok = QInputDialog.getText(self, "编辑分类", "请输入新名称:", text=old_name)
        if ok and name and name != old_name:
            from database import Database
            db = Database()

            # 更新数据库
            db.conn.execute("UPDATE categories SET name = ? WHERE id = ?", (name, cat_id))
            db.conn.commit()
            db.close()

            # 刷新列表
            self.categories = db.get_categories()
            self._load_categories()

    def _on_delete(self):
        selected = self.tree.selectedItems()
        if not selected:
            return

        item = selected[0]
        cat_id = item.data(0, Qt.UserRole)

        reply = QMessageBox.question(
            self, "确认删除",
            "确定要删除此分类吗？所有子分类和关联的密码也将被删除！",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                from database import Database
                db = Database()

                # 先删除子分类
                db.conn.execute("DELETE FROM categories WHERE parent_id = ?", (cat_id,))

                # 删除关联密码
                db.conn.execute("DELETE FROM password_entries WHERE category_id = ?", (cat_id,))

                # 最后删除主分类
                db.conn.execute("DELETE FROM categories WHERE id = ?", (cat_id,))

                db.conn.commit()
                db.close()

                # 刷新列表
                self.categories = db.get_categories()
                self._load_categories()
            except Exception as e:
                QMessageBox.critical(self, "错误", f"删除失败: {str(e)}")