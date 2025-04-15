"""
@Author: Henve
@Date: 2025/4/15 14:32
@File: main_window.py
@Description: 
"""

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
                             QTreeView, QTableView, QLineEdit, QPushButton, QLabel,
                             QMessageBox, QInputDialog, QMenu, QAction, QAbstractItemView)
from PyQt5.QtCore import Qt, QModelIndex, pyqtSignal, QSize
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon, QPixmap
from models.password_model import PasswordTableModel
from models.category_model import CategoryTreeModel


class MainWindow(QMainWindow):
    def __init__(self, db, crypto):
        super().__init__()
        self.db = db
        self.crypto = crypto
        self.current_category_id = None

        self.setWindowTitle("密码管理器")
        self.setGeometry(100, 100, 1000, 600)

        self._setup_ui()
        self._load_data()
        self._connect_signals()

    def _setup_ui(self):
        # 主窗口布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # 搜索栏
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索...")
        search_button = QPushButton("搜索")
        search_button.clicked.connect(self._on_search)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_button)

        # 操作按钮
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("新增")
        self.edit_button = QPushButton("编辑")
        self.delete_button = QPushButton("删除")
        self.export_button = QPushButton("导出数据")
        self.import_button = QPushButton("导入数据")
        self.change_password_button = QPushButton("修改主密码")
        self.manage_categories_button = QPushButton("管理分类")

        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addStretch()
        button_layout.addWidget(self.export_button)
        button_layout.addWidget(self.import_button)
        button_layout.addWidget(self.manage_categories_button)
        button_layout.addWidget(self.change_password_button)

        # 主内容区域 (分类树 + 密码列表)
        splitter = QSplitter()

        # 左侧分类树
        self.category_tree = QTreeView()
        self.category_tree.setHeaderHidden(True)
        self.category_tree.setSelectionBehavior(QTreeView.SelectRows)
        splitter.addWidget(self.category_tree)

        # 右侧密码列表
        self.password_table = QTableView()
        self.password_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.password_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.password_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        splitter.addWidget(self.password_table)

        splitter.setSizes([200, 600])

        # 添加到主布局
        main_layout.addLayout(search_layout)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(splitter)

        # 状态栏
        self.statusBar().showMessage("就绪")

    def _load_data(self):
        # 加载分类树
        categories = self.db.get_categories()
        self.category_model = CategoryTreeModel(categories)
        self.category_tree.setModel(self.category_model)
        self.category_tree.expandAll()

        # 加载密码列表
        self._load_password_data()

    def _load_password_data(self, search_term=None, category_id=None):
        password_data = self.db.get_password_entries(search_term)

        if category_id:
            password_data = [entry for entry in password_data if entry['category_id'] == category_id]

        # 创建模型并设置数据
        self.password_model = PasswordTableModel(password_data)
        self.password_table.setModel(self.password_model)

        # 隐藏密码列
        self.password_table.setColumnHidden(4, True)

        # 调整列宽
        self.password_table.horizontalHeader().setStretchLastSection(True)
        self.password_table.resizeColumnsToContents()

    def _connect_signals(self):
        # 按钮信号
        self.add_button.clicked.connect(self._on_add)
        self.edit_button.clicked.connect(self._on_edit)
        self.delete_button.clicked.connect(self._on_delete)
        self.export_button.clicked.connect(self._on_export)
        self.import_button.clicked.connect(self._on_import)
        self.change_password_button.clicked.connect(self._on_change_password)
        self.manage_categories_button.clicked.connect(self._on_manage_categories)

        # 分类树选择变化
        self.category_tree.selectionModel().selectionChanged.connect(self._on_category_selected)

        # 密码表双击事件
        self.password_table.doubleClicked.connect(self._on_edit)

    def _on_search(self):
        search_term = self.search_input.text().strip()
        self._load_password_data(search_term, self.current_category_id)

    def _on_category_selected(self):
        selected_index = self.category_tree.currentIndex()
        if selected_index.isValid():
            category_id = selected_index.data(Qt.UserRole)
            self.current_category_id = category_id
            self._load_password_data(None, category_id)

    def _on_add(self):
        from ui.password_dialog import PasswordDialog
        dialog = PasswordDialog(mode='add', categories=self.db.get_categories())
        if dialog.exec_() == PasswordDialog.Accepted:
            entry_data = dialog.get_entry_data()

            # 加密密码
            encrypted_password = self.crypto.encrypt_password(entry_data['password'])
            entry_data['encrypted_password'] = encrypted_password
            del entry_data['password']

            # 添加到数据库
            self.db.add_password_entry(entry_data)
            self._load_password_data(None, self.current_category_id)
            self.statusBar().showMessage("添加成功", 3000)

    def _on_edit(self):
        selected_indexes = self.password_table.selectionModel().selectedRows()
        if not selected_indexes:
            QMessageBox.warning(self, "警告", "请选择要编辑的条目")
            return

        row = selected_indexes[0].row()
        entry_id = self.password_model.data[row]['id']

        # 从数据库获取完整数据
        entries = self.db.get_password_entries()
        entry = next((e for e in entries if e['id'] == entry_id), None)
        if not entry:
            QMessageBox.warning(self, "错误", "找不到选定的条目")
            return

        # 解密密码
        try:
            decrypted_password = self.crypto.decrypt_password(entry['encrypted_password'])
        except Exception as e:
            QMessageBox.critical(self, "错误", f"解密失败: {str(e)}")
            return

        entry['password'] = decrypted_password

        from ui.password_dialog import PasswordDialog
        dialog = PasswordDialog(
            mode='edit',
            categories=self.db.get_categories(),
            entry_data=entry
        )

        if dialog.exec_() == PasswordDialog.Accepted:
            updated_data = dialog.get_entry_data()

            # 如果密码被修改，重新加密
            if updated_data['password'] != decrypted_password:
                encrypted_password = self.crypto.encrypt_password(updated_data['password'])
                updated_data['encrypted_password'] = encrypted_password
            else:
                updated_data['encrypted_password'] = entry['encrypted_password']

            del updated_data['password']

            # 更新数据库
            self.db.update_password_entry(entry_id, updated_data)
            self._load_password_data(None, self.current_category_id)
            self.statusBar().showMessage("更新成功", 3000)

    def _on_delete(self):
        selected_indexes = self.password_table.selectionModel().selectedRows()
        if not selected_indexes:
            QMessageBox.warning(self, "警告", "请选择要删除的条目")
            return

        row = selected_indexes[0].row()
        entry_id = self.password_model.data[row]['id']

        reply = QMessageBox.question(
            self, "确认删除",
            "确定要删除选定的条目吗？",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.db.delete_password_entry(entry_id)
            self._load_password_data(None, self.current_category_id)
            self.statusBar().showMessage("删除成功", 3000)

    def _on_export(self):
        from PyQt5.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出数据", "", "Database Files (*.db)"
        )

        if file_path:
            try:
                self.db.export_data(file_path)
                QMessageBox.information(self, "成功", "数据导出成功")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"导出失败: {str(e)}")

    def _on_import(self):
        from PyQt5.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getOpenFileName(
            self, "导入数据", "", "Database Files (*.db)"
        )

        if file_path:
            reply = QMessageBox.question(
                self, "确认导入",
                "导入将覆盖当前所有数据，确定要继续吗？",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                try:
                    self.db.import_data(file_path)
                    self._load_data()
                    QMessageBox.information(self, "成功", "数据导入成功")
                except Exception as e:
                    QMessageBox.critical(self, "错误", f"导入失败: {str(e)}")

    def _on_change_password(self):
        from ui.login_dialog import LoginDialog
        dialog = LoginDialog(mode='change', crypto=self.crypto)
        if dialog.exec_() == LoginDialog.Accepted:
            QMessageBox.information(self, "成功", "主密码修改成功")

    def _on_manage_categories(self):
        from ui.category_dialog import CategoryDialog
        dialog = CategoryDialog(self.db.get_categories())
        if dialog.exec_() == CategoryDialog.Accepted:
            # 重新加载分类数据
            categories = self.db.get_categories()
            self.category_model = CategoryTreeModel(categories)
            self.category_tree.setModel(self.category_model)
            self.category_tree.expandAll()
            self.statusBar().showMessage("分类已更新", 3000)