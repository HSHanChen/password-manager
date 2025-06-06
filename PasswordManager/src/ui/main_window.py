"""
@Author: Chan Sheen
@Date: 2025/4/15 16:22
@File: main_window.py
@Description: 
"""

import os

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QTreeView, QTableView, QHeaderView,
    QLineEdit, QPushButton, QMessageBox, QFileDialog, QDialog
)

from core.models import PasswordTableModel, CategoryTreeModel


class MainWindow(QMainWindow):
    def __init__(self, storage, config):
        super().__init__()
        self.storage = storage
        self.config = config
        self.current_category_id = None

        self.setWindowTitle("密码管理器")
        self.setGeometry(100, 100, 1000, 600)
        self.setMinimumSize(800, 500)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, False)

        self._setup_ui()
        self._load_data()
        self._connect_signals()

        print("主窗口初始化完成")

    def _setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索...")
        search_button = QPushButton("搜索")
        search_button.clicked.connect(self._on_search)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_button)

        splitter = QSplitter()
        self.category_tree = QTreeView()
        self.category_tree.setHeaderHidden(True)
        self.category_tree.setSelectionBehavior(QTreeView.SelectionBehavior.SelectRows)
        splitter.addWidget(self.category_tree)

        self.password_table = QTableView()
        self.password_table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.password_table.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        splitter.addWidget(self.password_table)
        splitter.setSizes([200, 600])

        toolbar_layout = QHBoxLayout()
        self.add_button = QPushButton("添加")
        self.edit_button = QPushButton("编辑")
        self.delete_button = QPushButton("删除")
        toolbar_layout.addWidget(self.add_button)
        toolbar_layout.addWidget(self.edit_button)
        toolbar_layout.addWidget(self.delete_button)

        main_layout.addLayout(search_layout)
        main_layout.addWidget(splitter)
        main_layout.addLayout(toolbar_layout)

        self._create_menu_bar()
        self.statusBar().showMessage("就绪")

    def _create_menu_bar(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu("文件")
        export_action = QAction("导出数据", self)
        export_action.triggered.connect(self._on_export)
        file_menu.addAction(export_action)

        import_action = QAction("导入数据", self)
        import_action.triggered.connect(self._on_import)
        file_menu.addAction(import_action)

        file_menu.addSeparator()
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        edit_menu = menubar.addMenu("编辑")
        add_action = QAction("添加密码", self)
        add_action.triggered.connect(self._on_add)
        edit_menu.addAction(add_action)

        edit_action = QAction("编辑密码", self)
        edit_action.triggered.connect(self._on_edit)
        edit_menu.addAction(edit_action)

        delete_action = QAction("删除密码", self)
        delete_action.triggered.connect(self._on_delete)
        edit_menu.addAction(delete_action)

        settings_menu = menubar.addMenu("设置")
        change_pw_action = QAction("修改主密码", self)
        change_pw_action.triggered.connect(self._on_change_password)
        settings_menu.addAction(change_pw_action)

    def _load_data(self):
        data = self.storage.load_data()
        self.category_model = CategoryTreeModel(data.get("categories", []))
        self.category_tree.setModel(self.category_model)
        self.category_tree.expandAll()
        self._load_password_data()

    def _load_password_data(self, search_term=None):
        data = self.storage.load_data()
        passwords = data.get("passwords", [])

        if search_term:
            search_term = search_term.lower()
            passwords = [
                p for p in passwords
                if any(search_term in p.get(field, '').lower() for field in ['name', 'url', 'username', 'notes'])
            ]

        if self.current_category_id:
            passwords = [p for p in passwords if p.get('category_id') == self.current_category_id]

        self.password_model = PasswordTableModel(passwords, data.get("categories", []))
        self.password_table.setModel(self.password_model)

        header = self.password_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setStretchLastSection(True)

    def _connect_signals(self):
        self.add_button.clicked.connect(self._on_add)
        self.edit_button.clicked.connect(self._on_edit)
        self.delete_button.clicked.connect(self._on_delete)
        self.category_tree.selectionModel().selectionChanged.connect(self._on_category_selected)
        self.password_table.doubleClicked.connect(self._on_edit)

    def _on_category_selected(self):
        selected = self.category_tree.currentIndex()
        if selected.isValid():
            self.current_category_id = selected.data(Qt.ItemDataRole.UserRole)
            self._load_password_data()
            self.statusBar().showMessage(f"已选择分类: {selected.data()}", 3000)

    def _on_search(self):
        search_term = self.search_input.text().strip()
        self._load_password_data(search_term)

    def _on_add(self):
        from ui.dialogs.password import PasswordDialog
        dialog = PasswordDialog(mode='add', categories=self.storage.load_data().get("categories", []))

        if dialog.exec() == QDialog.DialogCode.Accepted:
            entry = dialog.get_entry_data()
            encrypted = self.storage.encrypt_data({
                'password': entry['password']
            })

            new_entry = {
                'name': entry['name'],
                'url': entry['url'],
                'username': entry['username'],
                'encrypted_password': encrypted,
                'notes': entry['notes'],
                'category_id': entry['category_id']
            }

            data = self.storage.load_data()
            data.setdefault("passwords", []).append(new_entry)
            self.storage.save_data(data)
            self._load_password_data()
            self.statusBar().showMessage("添加成功", 3000)

    def _on_edit(self):
        selected = self.password_table.selectionModel().selectedRows()
        if not selected:
            QMessageBox.warning(self, "警告", "请先选择要编辑的条目")
            return

        row = selected[0].row()
        data = self.storage.load_data()
        entry = data["passwords"][row]

        try:
            decrypted = self.storage.decrypt_data(entry['encrypted_password'])
            password = decrypted.get('password', '')
        except Exception as e:
            QMessageBox.critical(self, "错误", f"解密失败: {str(e)}")
            return

        from ui.dialogs.password import PasswordDialog
        dialog = PasswordDialog(
            mode='edit',
            categories=data.get("categories", []),
            entry_data={
                'name': entry['name'],
                'url': entry['url'],
                'username': entry['username'],
                'password': password,
                'notes': entry.get('notes', ''),
                'category_id': entry.get('category_id')
            }
        )

        if dialog.exec() == QDialog.DialogCode.Accepted:
            updated = dialog.get_entry_data()
            if updated['password'] != password:
                entry['encrypted_password'] = self.storage.encrypt_data({'password': updated['password']})
            entry.update({
                'name': updated['name'],
                'url': updated['url'],
                'username': updated['username'],
                'notes': updated['notes'],
                'category_id': updated['category_id']
            })

            self.storage.save_data(data)
            self._load_password_data()
            self.statusBar().showMessage("更新成功", 3000)

    def _on_delete(self):
        selected = self.password_table.selectionModel().selectedRows()
        if not selected:
            QMessageBox.warning(self, "警告", "请先选择要删除的条目")
            return

        row = selected[0].row()
        data = self.storage.load_data()
        entry_name = data["passwords"][row]['name']

        reply = QMessageBox.question(self, "确认删除", f"确定要删除 '{entry_name}' 吗？",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            data["passwords"].pop(row)
            self.storage.save_data(data)
            self._load_password_data()
            self.statusBar().showMessage("删除成功", 3000)

    def _on_export(self):
        path, _ = QFileDialog.getSaveFileName(self, "导出数据", os.path.expanduser("~/password_backup.dat"), "Data Files (*.dat)")
        if path:
            try:
                import shutil
                shutil.copy2(self.config.data_path, path)
                QMessageBox.information(self, "成功", f"数据已导出到: {path}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"导出失败: {str(e)}")

    def _on_import(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择备份文件", os.path.expanduser("~"), "Data Files (*.dat)")
        if path:
            reply = QMessageBox.question(self, "确认导入", "导入将覆盖当前所有数据，确定继续吗？",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    import shutil
                    shutil.copy2(path, self.config.data_path)
                    # reload & reinitialize key
                    self._load_data()
                    QMessageBox.information(self, "成功", "数据导入完成")
                except Exception as e:
                    QMessageBox.critical(self, "错误", f"导入失败: {str(e)}")

    def _on_change_password(self):
        from ui.dialogs.login import LoginDialog
        dialog = LoginDialog(mode='change', crypto=self.storage)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            QMessageBox.information(self, "成功", "主密码已修改")

    def closeEvent(self, event):
        print("主窗口关闭")
        event.accept()
