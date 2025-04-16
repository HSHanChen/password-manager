"""
@Author: Chan Sheen
@Date: 2025/4/15 16:22
@File: main_window.py
@Description: 
"""

import os

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QSplitter, QTreeView, QTableView, QHeaderView,
                             QLineEdit, QPushButton, QAction,
                             QMessageBox, QFileDialog)

from core.models import PasswordTableModel, CategoryTreeModel


class MainWindow(QMainWindow):
    def __init__(self, storage, config):
        super().__init__()
        self.storage = storage
        self.config = config
        self.current_category_id = None

        # 窗口设置
        self.setWindowTitle("密码管理器")
        self.setGeometry(100, 100, 1000, 600)
        self.setMinimumSize(800, 500)
        self.setAttribute(Qt.WA_DeleteOnClose, False)  # 防止窗口被自动销毁

        # 初始化UI
        self._setup_ui()
        self._load_data()
        self._connect_signals()

        print("主窗口初始化完成")

    def _setup_ui(self):
        """初始化主界面"""
        # 主窗口中心部件
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

        # 主内容区域
        splitter = QSplitter()

        # 左侧分类树
        self.category_tree = QTreeView()
        self.category_tree.setHeaderHidden(True)
        self.category_tree.setSelectionBehavior(QTreeView.SelectRows)
        splitter.addWidget(self.category_tree)

        # 右侧密码表格
        self.password_table = QTableView()
        self.password_table.setSelectionBehavior(QTableView.SelectRows)
        self.password_table.setSelectionMode(QTableView.SingleSelection)
        splitter.addWidget(self.password_table)

        splitter.setSizes([200, 600])

        # 按钮工具栏
        toolbar_layout = QHBoxLayout()
        self.add_button = QPushButton("添加")
        self.edit_button = QPushButton("编辑")
        self.delete_button = QPushButton("删除")
        toolbar_layout.addWidget(self.add_button)
        toolbar_layout.addWidget(self.edit_button)
        toolbar_layout.addWidget(self.delete_button)

        # 组装主布局
        main_layout.addLayout(search_layout)
        main_layout.addWidget(splitter)
        main_layout.addLayout(toolbar_layout)

        # 创建菜单栏
        self._create_menu_bar()

        # 状态栏
        self.statusBar().showMessage("就绪")

    def _create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()

        # 文件菜单
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

        # 编辑菜单
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

        # 设置菜单
        settings_menu = menubar.addMenu("设置")

        change_pw_action = QAction("修改主密码", self)
        change_pw_action.triggered.connect(self._on_change_password)
        settings_menu.addAction(change_pw_action)

    def _load_data(self):
        """加载数据"""
        data = self.storage.load_data()

        # 加载分类树
        self.category_model = CategoryTreeModel(data["categories"])
        self.category_tree.setModel(self.category_model)
        self.category_tree.expandAll()

        # 加载密码表格
        self._load_password_data()

    def _load_password_data(self, search_term=None):
        """加载密码数据到表格"""
        data = self.storage.load_data()
        passwords = data["passwords"]

        # 应用搜索筛选
        if search_term:
            search_term = search_term.lower()
            passwords = [
                p for p in passwords
                if (search_term in p.get('name', '').lower() or
                    search_term in p.get('url', '').lower() or
                    search_term in p.get('username', '').lower() or
                    search_term in p.get('notes', '').lower())
            ]

        # 应用分类筛选
        if self.current_category_id:
            passwords = [p for p in passwords if p.get('category_id') == self.current_category_id]

        # 创建表格模型
        self.password_model = PasswordTableModel(passwords, data["categories"])
        self.password_table.setModel(self.password_model)

        # 调整表格列宽
        header = self.password_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setStretchLastSection(True)

    def _connect_signals(self):
        """连接信号与槽"""
        # 按钮信号
        self.add_button.clicked.connect(self._on_add)
        self.edit_button.clicked.connect(self._on_edit)
        self.delete_button.clicked.connect(self._on_delete)

        # 分类树选择变化
        self.category_tree.selectionModel().selectionChanged.connect(
            self._on_category_selected)

        # 表格双击事件
        self.password_table.doubleClicked.connect(self._on_edit)

    def _on_category_selected(self):
        """分类选择变化处理"""
        selected = self.category_tree.currentIndex()
        if selected.isValid():
            self.current_category_id = selected.data(Qt.UserRole)
            self._load_password_data()
            self.statusBar().showMessage(f"已选择分类: {selected.data()}", 3000)

    def _on_search(self):
        """搜索处理"""
        search_term = self.search_input.text().strip()
        self._load_password_data(search_term)

    def _on_add(self):
        """添加密码条目"""
        from ui.dialogs.password import PasswordDialog
        dialog = PasswordDialog(
            mode='add',
            categories=self.storage.load_data()["categories"]
        )

        if dialog.exec_() == QDialog.Accepted:
            entry = dialog.get_entry_data()

            # 加密密码
            encrypted = self.storage.encrypt_data({
                'password': entry['password'],
                'iv': os.urandom(16).hex()
            })

            # 准备存储数据
            new_entry = {
                'name': entry['name'],
                'url': entry['url'],
                'username': entry['username'],
                'encrypted_password': encrypted,
                'notes': entry['notes'],
                'category_id': entry['category_id']
            }

            # 保存到存储
            data = self.storage.load_data()
            data["passwords"].append(new_entry)
            self.storage.save_data(data)

            # 刷新显示
            self._load_password_data()
            self.statusBar().showMessage("添加成功", 3000)

    def _on_edit(self):
        """编辑密码条目"""
        selected = self.password_table.selectionModel().selectedRows()
        if not selected:
            QMessageBox.warning(self, "警告", "请先选择要编辑的条目")
            return

        row = selected[0].row()
        data = self.storage.load_data()
        entry = data["passwords"][row]

        # 解密密码
        try:
            decrypted = self.storage.decrypt_data(entry['encrypted_password'])
            password = decrypted['password']
        except Exception as e:
            QMessageBox.critical(self, "错误", f"解密失败: {str(e)}")
            return

        from ui.dialogs.password import PasswordDialog
        dialog = PasswordDialog(
            mode='edit',
            categories=data["categories"],
            entry_data={
                'name': entry['name'],
                'url': entry['url'],
                'username': entry['username'],
                'password': password,
                'notes': entry.get('notes', ''),
                'category_id': entry.get('category_id')
            }
        )

        if dialog.exec_() == QDialog.Accepted:
            updated = dialog.get_entry_data()

            # 如果密码有变化，重新加密
            if updated['password'] != password:
                encrypted = self.storage.encrypt_data({
                    'password': updated['password'],
                    'iv': os.urandom(16).hex()
                })
                entry['encrypted_password'] = encrypted

            # 更新其他字段
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
        """删除密码条目"""
        selected = self.password_table.selectionModel().selectedRows()
        if not selected:
            QMessageBox.warning(self, "警告", "请先选择要删除的条目")
            return

        row = selected[0].row()
        data = self.storage.load_data()
        entry_name = data["passwords"][row]['name']

        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除 '{entry_name}' 吗？",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            data["passwords"].pop(row)
            self.storage.save_data(data)
            self._load_password_data()
            self.statusBar().showMessage("删除成功", 3000)

    def _on_export(self):
        """导出数据"""
        path, _ = QFileDialog.getSaveFileName(
            self, "导出数据",
            os.path.join(os.path.expanduser("~"), "password_backup.dat"),
            "Data Files (*.dat)"
        )

        if path:
            try:
                import shutil
                shutil.copy2(self.config.data_path, path)
                QMessageBox.information(self, "成功", f"数据已导出到: {path}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"导出失败: {str(e)}")

    def _on_import(self):
        """导入数据"""
        path, _ = QFileDialog.getOpenFileName(
            self, "选择备份文件",
            os.path.expanduser("~"),
            "Data Files (*.dat)"
        )

        if path:
            reply = QMessageBox.question(
                self, "确认导入",
                "导入将覆盖当前所有数据，确定继续吗？",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                try:
                    import shutil
                    shutil.copy2(path, self.config.data_path)

                    # 重新加载数据
                    self._load_data()
                    QMessageBox.information(self, "成功", "数据导入完成")
                except Exception as e:
                    QMessageBox.critical(self, "错误", f"导入失败: {str(e)}")

    def _on_change_password(self):
        """修改主密码"""
        from ui.dialogs.login import LoginDialog
        dialog = LoginDialog(mode='change', crypto=self.storage)
        if dialog.exec_() == QDialog.Accepted:
            QMessageBox.information(self, "成功", "主密码已修改")

    def closeEvent(self, event):
        """关闭事件处理"""
        print("主窗口关闭")
        event.accept()
