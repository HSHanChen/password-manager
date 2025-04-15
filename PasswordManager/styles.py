"""
@Author: Chan Sheen
@Date: 2025/4/15 16:21
@File: styles.py
@Description: 
"""


def get_stylesheet():
    return """
    /* 主窗口样式 */
    QMainWindow {
        background-color: #f0f2f5;
    }

    /* 按钮样式 */
    QPushButton {
        background-color: #4a6fa5;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 4px;
        min-width: 80px;
        font-size: 12px;
    }

    QPushButton:hover {
        background-color: #3a5a8f;
    }

    QPushButton:pressed {
        background-color: #2a4a7f;
    }

    /* 输入框样式 */
    QLineEdit, QComboBox {
        border: 1px solid #d1d5db;
        border-radius: 4px;
        padding: 6px;
        background: white;
        selection-background-color: #4a6fa5;
    }

    /* 表格样式 */
    QTableView {
        background: white;
        border: 1px solid #d1d5db;
        gridline-color: #e5e7eb;
        selection-background-color: #e3f2fd;
    }

    QHeaderView::section {
        background-color: #4a6fa5;
        color: white;
        padding: 6px;
        border: none;
    }

    /* 菜单栏样式 */
    QMenuBar {
        background-color: #e0e7ff;
        padding: 4px;
    }

    QMenuBar::item {
        padding: 4px 10px;
        background: transparent;
        border-radius: 4px;
    }

    QMenuBar::item:selected {
        background: #c7d2fe;
    }

    /* 对话框样式 */
    QDialog {
        background: #f0f2f5;
    }

    /* 状态栏样式 */
    QStatusBar {
        background: #e0e7ff;
        color: #374151;
    }
    """