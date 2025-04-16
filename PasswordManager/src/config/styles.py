"""
@Author: Chan Sheen
@Date: 2025/4/15 16:21
@File: styles.py
@Description: 
"""


# 加载并应用样式表
def load_stylesheet():
    try:
        with open("../resources/qss/main.qss", "r", encoding="utf-8") as style_file:
            return style_file.read()
    except FileNotFoundError:
        return ""  # 如果找不到样式表，返回空样式
