'''
右键菜单，具体功能有待完善
'''
import os
import tkinter as tk
import tkinter.messagebox


class RightClickMenu(object):
    def __init__(self, parent=None):
        self.widget = parent
        self.menu = tk.Menu(parent, tearoff=0)

        self.menu.add_command(label="删除", command=self.on_delete)
        # self.menu.add_command(label="Paste", command=self.on_paste)
        # self.menu.add_separator()
        # self.menu.add_command(label="Cut", command=self.on_cut)

    def popupmenu(self, event):
        self.menu.post(event.x_root, event.y_root)

    def on_delete(self):
        selected_item = self.widget.selection()
        # self.widget.delete(selected_item)
        file_path = os.path.abspath("./reportdata")
        if self.widget.parent(selected_item):  # 存在父控件
            directory_id = self.widget.parent(selected_item)
            directory_name = self.widget.item(directory_id)['text']
            file_name = self.widget.item(selected_item)['text']
            path = os.path.join(file_path, directory_name)
            path = os.path.join(path, file_name)
            if os.path.exists(path):
                # TODO:是不是应该改用模态窗口呢？？？
                if tkinter.messagebox.askokcancel('提示', '回测文件将被删除'):
                    os.remove(path)
                    self.widget.delete(selected_item)
        else:
            directory_name = self.widget.item(selected_item)['text']
            path = os.path.join(file_path, directory_name)
            if os.path.exists(path):
                if tkinter.messagebox.askokcancel('提示', '整个文件夹将被删除'):
                    os.removedirs(path)
                    self.widget.delete(selected_item)

    def on_paste(self):
        pass

    def on_cut(self):
        pass
