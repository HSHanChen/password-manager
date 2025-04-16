"""
@Author: Chan Sheen
@Date: 2025/4/15 16:21
@File: styles.py
@Description: 
"""

from PyQt6.QtCore import QFile, QTextStream


def load_stylesheet():
    style_file = QFile(":/qss/main.qss")
    if style_file.open(QFile.ReadOnly | QFile.Text):
        stream = QTextStream(style_file)
        return stream.readAll()
    return """
    QMainWindow {
        background-color: #f5f5f5;
    }
    QStatusBar {
        background: #e0e7ff;
    }
    /* 其他默认样式 */
    """
