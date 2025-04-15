"""
@Author: Chan Sheen
@Date: 2025/4/15 16:22
@File: main_window.py
@Description: 
"""
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QSplitter,
                             QTreeView, QTableView)


class MainWindow(QMainWindow):
    def __init__(self, storage, config):
        super().__init__()
        self.storage = storage
        self.config = config
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        self.setWindowTitle("密码管理器")
        self.setGeometry(100, 100, 1000, 600)

        # 主布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 分割视图
        splitter = QSplitter()

        # 分类树
        self.category_tree = QTreeView()
        splitter.addWidget(self.category_tree)

        # 密码表格
        self.password_table = QTableView()
        splitter.addWidget(self.password_table)

        layout.addWidget(splitter)

        # 状态栏
        self.statusBar().showMessage("就绪")

        # 菜单栏
        self.create_menus()

    def create_menus(self):
        menubar = self.menuBar()

        # 文件菜单
        file_menu = menubar.addMenu("文件")
        file_menu.addAction("导入数据")
        file_menu.addAction("导出数据")
        file_menu.addSeparator()
        file_menu.addAction("退出", self.close)

        # 编辑菜单
        edit_menu = menubar.addMenu("编辑")
        edit_menu.addAction("添加密码", self.add_password)
        edit_menu.addAction("编辑密码", self.edit_password)
        edit_menu.addAction("删除密码", self.delete_password)

        # 设置菜单
        settings_menu = menubar.addMenu("设置")
        settings_menu.addAction("数据位置", self.change_data_location)
        settings_menu.addAction("修改密码", self.change_master_password)

    def load_data(self):
        data = self.storage.load_data()
        # 加载分类和密码数据
        # ...

    # 其他方法...
