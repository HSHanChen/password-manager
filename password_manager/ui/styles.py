"""
@Author: Henve
@Date: 2025/4/15 15:22
@File: styles.py
@Description: 
"""

def get_style_sheet():
    return """
    QMainWindow {
        background-color: #f5f5f5;
    }

    QTreeView, QTableView {
        background-color: white;
        border: 1px solid #dcdcdc;
        border-radius: 4px;
        padding: 2px;
    }

    QPushButton {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 6px 12px;
        border-radius: 4px;
        min-width: 80px;
    }

    QPushButton:hover {
        background-color: #45a049;
    }

    QPushButton:pressed {
        background-color: #3d8b40;
    }

    QLineEdit {
        border: 1px solid #dcdcdc;
        border-radius: 4px;
        padding: 5px;
    }

    QMenuBar {
        background-color: #e0e0e0;
    }

    QMenuBar::item {
        padding: 5px 10px;
        background: transparent;
    }

    QMenuBar::item:selected {
        background: #d0d0d0;
    }

    QMenu {
        background-color: white;
        border: 1px solid #dcdcdc;
    }

    QMenu::item:selected {
        background-color: #4CAF50;
        color: white;
    }

    QStatusBar {
        background-color: #e0e0e0;
    }
    """