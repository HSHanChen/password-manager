"""
@Author: Chan Sheen
@Date: 2025/4/14 11:52
@File: main.py
@Description: 程序入口
"""

import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox
from core.storage import load_data, save_data
import os
import io
import cairosvg
from PIL import Image, ImageTk


class PasswordManagerApp:
    def set_global_font():
        style = tb.Style()
        style.configure('.', font=('Microsoft YaHei', 12))  # 设置全局字体为微软雅黑，大小12

    def __init__(self, root):
        self.root = root
        self.root.title("密码管理器")

        # 获取屏幕的宽度和高度
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # 设置窗口大小
        window_width = int(screen_width * 0.8)
        window_height = int(screen_height * 0.8)

        # 计算窗口左上角的坐标，使窗口居中
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        self.master_password = ""
        self.passwords = []

        self.main_frame = tb.Frame(root)
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.main_frame.rowconfigure(2, weight=1)
        self.main_frame.columnconfigure(0, weight=1)

        self.password_var = tb.StringVar()
        tb.Label(self.main_frame, text="主密码:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        tb.Entry(self.main_frame, textvariable=self.password_var, show="*", width=30).grid(row=0, column=1, padx=5, pady=5)
        tb.Button(self.main_frame, text="加载密码", command=self.load_passwords, bootstyle=PRIMARY).grid(row=0, column=2, padx=5)

        self.columns = ("name", "url", "username", "password", "remark")
        self.tree = tb.Treeview(self.main_frame, columns=self.columns, show="headings", bootstyle=INFO)

        column_titles = {
            "name": "名称",
            "url": "地址",
            "username": "账号",
            "password": "密码",
            "remark": "备注"
        }

        for col in self.columns:
            self.tree.heading(col, text=column_titles.get(col, col))
            self.tree.column(col, width=200 if col != "password" else 100, anchor="center")

        self.tree.grid(row=2, column=0, columnspan=3, sticky="nsew", padx=10, pady=10)

        button_frame = tb.Frame(self.main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=10)
        tb.Button(button_frame, text="添加", command=self.add_password, bootstyle=SUCCESS).pack(side="left", padx=5)
        tb.Button(button_frame, text="修改", command=self.edit_password, bootstyle=WARNING).pack(side="left", padx=5)
        tb.Button(button_frame, text="删除", command=self.delete_password, bootstyle=DANGER).pack(side="left", padx=5)

    def load_passwords(self):
        try:
            self.master_password = self.password_var.get()
            self.passwords = load_data(self.master_password)
            self.refresh_table()
        except Exception as e:
            messagebox.showerror("错误", f"加载失败：{str(e)}")

    def refresh_table(self):
        self.tree.delete(*self.tree.get_children())
        for item in self.passwords:
            self.tree.insert("", "end", values=(
                item["name"],
                item["url"],
                item["username"],
                "******",
                item["remark"]
            ))

    def add_password(self):
        self.open_editor("添加密码")

    def edit_password(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选择一条记录")
            return
        index = self.tree.index(selected[0])
        self.open_editor("修改密码", index)

    def delete_password(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选择一条记录")
            return
        index = self.tree.index(selected[0])
        del self.passwords[index]
        save_data(self.passwords, self.master_password)
        self.refresh_table()

    def open_editor(self, title, index=None):
        edit_window = tb.Toplevel(self.root)
        edit_window.title(title)
        window_width = int(self.root.winfo_width() * 0.6)
        window_height = int(self.root.winfo_height() * 0.6)
        x = (self.root.winfo_screenwidth() - window_width) // 2
        y = (self.root.winfo_screenheight() - window_height) // 2
        edit_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        edit_window.resizable(False, False)

        for i in range(4):
            edit_window.columnconfigure(i, weight=1)

        pad_y = 15

        name_var = tb.StringVar()
        url_var = tb.StringVar()
        user_var = tb.StringVar()
        pwd_var = tb.StringVar()
        remark_var = tb.StringVar()

        if index is not None:
            item = self.passwords[index]
            name_var.set(item["name"])
            url_var.set(item["url"])
            user_var.set(item["username"])
            pwd_var.set(item["password"])
            remark_var.set(item["remark"])

        def add_centered_entry(row, label, var, is_password=False):

            # 分离文字和星号
            label_text = f"{label}"  # 字段名称部分
            star_text = " *"  # 必填星号部分

            # 创建一个Frame容器，用来包裹两个标签
            label_frame = tb.Frame(edit_window)

            # 创建显示字段名称的标签
            label_widget = tb.Label(label_frame, text=label_text)
            label_widget.pack(side="left")  # 文字部分

            # 创建显示红色星号的标签
            star_widget = tb.Label(label_frame, text=star_text, foreground="red")  # 红色星号
            star_widget.pack(side="left")  # 星号部分

            # 放置Frame
            label_frame.grid(row=row, column=1, sticky="e", pady=pad_y)

            # tb.Label(edit_window, text=label).grid(row=row, column=1, sticky="e", pady=pad_y)
            if is_password:
                frame = tb.Frame(edit_window)
                entry = tb.Entry(frame, textvariable=var, width=70, show="*")
                entry.pack(side="left", padx=(0, 5))

                with open("assets/eye.svg", "rb") as f:
                    svg_data = f.read()
                png_data = cairosvg.svg2png(bytestring=svg_data, output_width=15, output_height=15)
                eye_img = Image.open(io.BytesIO(png_data))
                eye_icon = ImageTk.PhotoImage(eye_img)

                def toggle_password():
                    entry.config(show="" if entry.cget("show") == "*" else "*")

                label = tb.Label(frame, image=eye_icon, cursor="hand2")
                label.image = eye_icon
                label.pack(side="left")
                label.bind("<Button-1>", lambda e: toggle_password())
                frame.grid(row=row, column=2, sticky="w")
                return entry
            else:
                entry = tb.Entry(edit_window, textvariable=var, width=70)
                entry.grid(row=row, column=2, sticky="w", pady=pad_y)
                return entry

        add_centered_entry(0, "名称", name_var)
        add_centered_entry(1, "地址", url_var)
        add_centered_entry(2, "账号", user_var)
        add_centered_entry(3, "密码", pwd_var, is_password=True)

        tb.Label(edit_window, text="备注").grid(row=4, column=1, sticky="ne", pady=pad_y)
        remark_text = tb.Text(edit_window, wrap="word", height=5, width=70)
        remark_text.grid(row=4, column=2, sticky="w", pady=pad_y)
        if remark_var.get():
            remark_text.insert("1.0", remark_var.get())

        def save():
            new_data = {
                "name": name_var.get(),
                "url": url_var.get(),
                "username": user_var.get(),
                "password": pwd_var.get(),
                "remark": remark_text.get("1.0", "end").strip()
            }
            if not all(new_data.values()):
                messagebox.showwarning("提示", "所有字段都不能为空")
                edit_window.focus_set()
                return

            if index is None:
                self.passwords.append(new_data)
            else:
                self.passwords[index] = new_data

            save_data(self.passwords, self.master_password)
            self.refresh_table()
            edit_window.destroy()


        tb.Button(edit_window, text="保存", command=save, bootstyle=SUCCESS).grid(row=5, column=1, columnspan=2, pady=pad_y, sticky="")


if __name__ == "__main__":
    if not os.path.exists("data"):
        os.makedirs("data")
    root = tb.Window(themename="flatly")
    app = PasswordManagerApp(root)
    root.mainloop()


