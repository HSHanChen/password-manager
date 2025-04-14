"""
@Author: Chan Sheen
@Date: 2025/4/14 11:52
@File: main.py
@Description: 程序入口
"""

import tkinter as tk
from tkinter import ttk, messagebox
from core.storage import load_data, save_data
import os
from tkinter import PhotoImage, Canvas


class PasswordManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("密码管理器")

        # 获取屏幕分辨率，设置主窗口为屏幕的 80%
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = int(screen_width * 0.8)
        window_height = int(screen_height * 0.8)
        self.root.geometry(f"{window_width}x{window_height}")

        # 设置窗口可自适应
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        self.master_password = ""
        self.passwords = []

        # 主 Frame
        self.main_frame = tk.Frame(root)
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.main_frame.rowconfigure(2, weight=1)
        self.main_frame.columnconfigure(0, weight=1)

        # 顶部密码框
        self.password_var = tk.StringVar()
        tk.Label(self.main_frame, text="主密码:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        tk.Entry(self.main_frame, textvariable=self.password_var, show="*", width=30).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(self.main_frame, text="加载密码", command=self.load_passwords).grid(row=0, column=2, padx=5)

        # 表格
        self.columns = ("name", "url", "username", "password", "remark")
        self.tree = ttk.Treeview(self.main_frame, columns=self.columns, show="headings")

        # 英文字段名 => 中文标题
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

        # 按钮区域
        button_frame = tk.Frame(self.main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=10)
        tk.Button(button_frame, text="添加", command=self.add_password).pack(side="left", padx=5)
        tk.Button(button_frame, text="修改", command=self.edit_password).pack(side="left", padx=5)
        tk.Button(button_frame, text="删除", command=self.delete_password).pack(side="left", padx=5)

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
                "******",  # 显示密码时加密显示
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
        import os
        from tkinter import PhotoImage

        edit_window = tk.Toplevel(self.root)
        edit_window.title(title)

        # 设置弹窗大小为主窗口的 60%
        window_width = int(self.root.winfo_width() * 0.6)
        window_height = int(self.root.winfo_height() * 0.6)
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        edit_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        edit_window.resizable(False, False)
        edit_window.config(bg="#f5f5f5")

        pad_x = 20
        pad_y = 15

        name_var = tk.StringVar()
        url_var = tk.StringVar()
        user_var = tk.StringVar()
        pwd_var = tk.StringVar()
        remark_var = tk.StringVar()

        if index is not None:
            item = self.passwords[index]
            name_var.set(item["name"])
            url_var.set(item["url"])
            user_var.set(item["username"])
            pwd_var.set(item["password"])
            remark_var.set(item["remark"])

        row = 0

        # 通用 Label + Entry 函数
        def add_entry(label, variable, r):
            tk.Label(edit_window, text=label, bg="#f5f5f5", font=("Segoe UI", 12)).grid(row=r, column=0, padx=pad_x, pady=pad_y, sticky="e")
            entry = tk.Entry(edit_window, textvariable=variable, width=50, font=("Segoe UI", 13), bd=2, relief="groove")
            entry.grid(row=r, column=1, padx=pad_x, pady=pad_y, sticky="w")
            return entry

        add_entry("名称", name_var, row);
        row += 1
        add_entry("地址", url_var, row);
        row += 1
        add_entry("账号", user_var, row);
        row += 1

        # 密码字段 + 眼睛图标
        tk.Label(edit_window, text="密码", bg="#f5f5f5", font=("Segoe UI", 12)).grid(row=row, column=0, padx=pad_x, pady=pad_y, sticky="e")
        password_frame = tk.Frame(edit_window, bg="#f5f5f5")
        password_frame.grid(row=row, column=1, sticky="w", padx=pad_x, pady=pad_y)

        password_entry = tk.Entry(password_frame, textvariable=pwd_var, show="*", width=44, font=("Segoe UI", 13), bd=2, relief="groove")
        password_entry.pack(side="left")

        try:
            eye_icon = PhotoImage(file=os.path.join("assets", "eye_icon.png")).subsample(15, 15)
        except Exception as e:
            print("图标加载失败:", e)
            eye_icon = None

        def toggle_password():
            if password_entry.cget("show") == "*":
                password_entry.config(show="")
            else:
                password_entry.config(show="*")

        if eye_icon:
            eye_label = tk.Label(password_frame, image=eye_icon, bg="#f5f5f5", cursor="hand2")
            eye_label.image = eye_icon  # 避免被垃圾回收
            eye_label.pack(side="left", padx=(5, 0))
            eye_label.bind("<Button-1>", lambda e: toggle_password())

        row += 1

        # 备注（Text）
        tk.Label(edit_window, text="备注", bg="#f5f5f5", font=("Segoe UI", 12)).grid(row=row, column=0, padx=pad_x, pady=pad_y, sticky="ne")
        remark_text = tk.Text(edit_window, wrap="word", height=4, width=50, font=("Segoe UI", 12), bd=2, relief="groove")
        remark_text.grid(row=row, column=1, padx=pad_x, pady=pad_y, sticky="w")
        if remark_var.get():
            remark_text.insert("1.0", remark_var.get())
        row += 1

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
                return

            if index is None:
                self.passwords.append(new_data)
            else:
                self.passwords[index] = new_data

            save_data(self.passwords, self.master_password)
            self.refresh_table()
            edit_window.destroy()

        # 保存按钮
        save_button = tk.Button(edit_window, text="保存", command=save, font=("Segoe UI", 12), bg="#4CAF50", fg="white", width=20)
        save_button.grid(row=row, column=1, pady=pad_y)

# 入口
if __name__ == "__main__":
    if not os.path.exists("data"):
        os.makedirs("data")
    root = tk.Tk()
    app = PasswordManagerApp(root)
    root.mainloop()



