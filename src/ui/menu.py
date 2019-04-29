import os
import sys
sys.path.append("..")

from tkinter import *
from tkinter import messagebox
import tkinter.ttk as ttk

from utils.language import Language
from .language import Language
from .com_view import NewDirToplevel, NewFileToplevel, RenameToplevel, DeleteToplevel


class StrategyMenu(object):
    def __init__(self, controller, parent=None):
        self._controller = controller
        self.widget = parent
        self.language = Language("EquantMainFrame")
        self.menu = Menu(parent, tearoff=0)
        self.selected_item = None
        self._rightClickPath = ""    # 记录右键弹出菜单时选中的策略路径

    def add_event(self):
        new_menu = Menu(self.menu, tearoff=0)
        if len(self.selected_item) == 1 and self.widget.parent(self.selected_item):  # 保证只选中一个
            self.menu.add_command(label="加载", command=self.runStrategy)
        self.menu.add_cascade(label="新建", menu=new_menu)
        new_menu.add_command(label=self.language.get_text(41), command=self.newStrategy)
        new_menu.add_command(label=self.language.get_text(42), command=self.newDir)
        if len(self.selected_item) == 1:
            self.menu.add_command(label="修改名称", command=self.rename)
        # self.menu.add_command(label="移动分组", command=self.move_strategy)
        self.menu.add_command(label="删除", command=self.delete_)

    def popupmenu(self, event):
        select = self.widget.identify_row(event.y)
        self.selected_item = event.widget.selection()

        self._rightClickPath = self.widget.item(select)["values"][0]

        if self.selected_item:
            if select:
                if select not in self.selected_item:
                    self.widget.focus(select)
                    self.widget.selection_set(select)
                    self.selected_item = event.widget.selection()
            self.add_event()
            self.menu.post(event.x_root, event.y_root)
        else:
            if select:
                self.widget.focus(select)
                self.widget.selection_set(select)
                self.selected_item = event.widget.selection()
                self.widget.focus(select)
                self.widget.selection_set(select)
                self.add_event()
                self.menu.post(event.x_root, event.y_root)

    def get_file_path(self):
        select = self.selected_item
        file_path = []
        for idx in select:
            file_path.append(self.widget.item(idx)["values"][0])
        return file_path

    def runStrategy(self):
        # 加载策略
        # TODO：进行操作前需要对当前选中的策略进行保存
        self._controller.load(self._rightClickPath)
        print("Run is ready")

    def newStrategy(self):
        newFileWin = NewFileToplevel(self._controller.top)

        def save_():
            # 新建策略前先保存当前选中的策略
            self._controller.saveStrategy()
            # TODO：目录树多选时path为list，新建文件的存储位置可能会有问题（总是新建到item最小的文件所在的文件夹）
            temp_path = self.get_file_path()
            print("temp_path: ", temp_path)
            path = temp_path[0]
            if os.path.isdir(path):
                dir_path = path
            if os.path.isfile(path):
                dir_path = os.path.dirname(path)
            file_name = newFileWin.nameEntry.get()
            file_type = newFileWin.type_chosen.get()
            if file_name == "":
                messagebox.showinfo(title=self.language.get_text(8), message=self.language.get_text(16))
            else:
                file = file_name + file_type
                if not os.path.exists(os.path.join(dir_path, file)):
                    filePath = os.path.join(dir_path, file)
                    self._controller.newStrategy(filePath)
                    # TODO：怎么把文件按文件名插入到合适的位置呢？
                    newFileWin.destroy()
                else:
                    messagebox.showinfo(self.language.get_text(8),
                                        self.language.get_text(17) + file + self.language.get_text(18))

        def cancel():
            newFileWin.destroy()

        newFileWin.saveBtn.configure(command=save_)
        newFileWin.cancelBtn.configure(command=cancel)
        # 模态窗口
        newFileWin.display()

    def newDir(self):
        newTop = NewDirToplevel(self._controller.top)

        def save():
            # 新建策略前先保存当前选中的策略
            self._controller.saveStrategy()

            tempPath = self.get_file_path()
            path =tempPath[0]
            if os.path.isdir(path):
                dir_path = path
            if os.path.isfile(path):
                dir_path = os.path.dirname(path)
            file_name = newTop.nameEntry.get()
            if file_name == "":
                messagebox.showinfo(self.language.get_text(8), self.language.get_text(22))
            else:
                if not os.path.exists(os.path.join(dir_path, file_name)):
                    filePath = os.path.join(dir_path, file_name)
                    # TODO: insert的位置问题。。。
                    # TODO：新建目录和新建文件在目录树种无法区别
                    self._controller.newDir(filePath)
                    newTop.destroy()
                else:
                    messagebox.showinfo(self.language.get_text(8),
                                        self.language.get_text(23) + file_name + self.language.get_text(24))

        def cancel():
            newTop.destroy()

        newTop.saveBtn.config(command=save)
        newTop.cancelBtn.config(command=cancel)
        newTop.display()

    def move_strategy(self):
        """移动文件"""
        # TODO: 可以用treeview的move方法实现吧
        # TODO：进行操作前需要对当前选中的策略进行保存
        pass

    def rename(self):
        """重命名文件"""
        # TODO：RenameToplevel的父控件是不是不太对啊

        tempPath = self.get_file_path()
        path = tempPath[0]
        renameTop = RenameToplevel(path, self._controller.top)

        def enter():
            # 新建策略前先保存当前选中的策略
            self._controller.saveStrategy()

            if not os.path.exists(path):
                messagebox.showinfo(self.language.get_text(8), self.language.get_text(31))
            else:
                if not os.path.exists(
                        os.path.join(os.path.dirname(path), renameTop.newEntry.get() + renameTop.typeChosen.get())):
                    fullPath = os.path.join(os.path.dirname(path), renameTop.newEntry.get()
                                             + renameTop.typeChosen.get())
                    self.widget.item(self.selected_item, values=[fullPath, "!@#$%^&*"])
                    os.rename(path, fullPath)

                    if os.path.isfile(fullPath):
                        text = renameTop.newEntry.get() + renameTop.typeChosen.get()
                        self.widget.item(self.selected_item, text=text)
                    if os.path.isdir(fullPath):
                        text = renameTop.newEntry.get()
                        self.widget.tag_configure(self.selected_item, text=text)
                    self.widget.update()
                if os.path.exists(os.path.join(os.path.dirname(path), renameTop.newEntry.get())):
                    messagebox.showinfo(self.language.get_text(8), self.language.get_text(32))
            renameTop.destroy()

        def cancel():
            renameTop.destroy()

        renameTop.saveBtn.config(command=enter)
        renameTop.cancelBtn.config(command=cancel)
        renameTop.display()

    def openDir(self):
        """打开文件夹"""
        # TODO：进行操作前需要对当前选中的策略进行保存
        pass

    def delete_(self):
        """删除文件"""
        # TODO: 若删除文件为当前选中文件，需要更新editor_head和editor_text，重置为空吧
        tempPath = self.get_file_path()
        deleteTop = DeleteToplevel(tempPath, self._controller.top)
        selected_item = self.selected_item
        # 当前选中的策略路径
        editorPath = self._controller.getEditorText()["path"]
        def enter():
            # 新建策略前先保存当前选中的策略
            self._controller.saveStrategy()
            for path, select in zip(tempPath, selected_item):
                if os.path.exists(path):
                    if os.path.isdir(path):
                        for root, dirs, files in os.walk(path):
                            for name in files:
                                deletePath = os.path.join(root, name)
                                if editorPath == deletePath:
                                    # 更新选中策略路径
                                    self._controller.setEditorTextCode("")
                                    # 更新策略编辑界面显示信息
                                    self._controller.updateEditor("")
                                    os.remove(deletePath)
                            for name in dirs:
                                os.rmdir(os.path.join(root, name))
                        self.widget.delete(select)
                    else:
                        if editorPath == path:
                            # 更新选中策略路径
                            self._controller.setEditorTextCode("")
                            # 更新策略编辑界面显示信息
                            self._controller.updateEditor("")

                        os.remove(path)
                        self.widget.delete(select)
                else:  # 文件不存在（本地文件已经删除）
                    self.widget.delete(select)

            deleteTop.destroy()

        def cancel():
            deleteTop.destroy()

        deleteTop.saveBtn.config(command=enter)
        deleteTop.cancelBtn.config(command=cancel)
        deleteTop.display()


class RunMenu(object):
    def __init__(self, controller, parent=None):
        self._controller = controller
        self.widget = parent
        self.menu = Menu(parent, tearoff=0)
        self.selected_item = None
        self._strategyId = []   # 策略Id列表，弹出右键菜单时赋值

    def add_event(self):
        self.menu.add_command(label="暂停", command=self.onPause)
        self.menu.add_command(label="停止", command=self.onQuit)
        self.menu.add_command(label="启动", command=self.onResume)
        self.menu.add_command(label="删除", command=self.onDelete)

    def popupmenu(self, event):
        select = self.widget.identify_row(event.y)
        self.selected_item = event.widget.selection()

        # 右键弹出菜单时给strategyId 赋值

        if self.selected_item:  # 选中之后右键弹出菜单
            for idx in self.selected_item:
                self._strategyId.append(idx)
        else:  # 没有选中，直接右键选择
            self._strategyId.append(select)

        if self.selected_item:
            if select:
                if select not in self.selected_item:
                    self.widget.focus(select)
                    self.widget.selection_set(select)
                    self.selected_item = event.widget.selection()
            self.add_event()
            self.menu.post(event.x_root, event.y_root)
        else:
            if select:
                self.widget.focus(select)
                self.widget.selection_set(select)
                self.selected_item = event.widget.selection()
                self.widget.focus(select)
                self.widget.selection_set(select)
                self.add_event()
                self.menu.post(event.x_root, event.y_root)

    #TODO:这三个函数怎么写到control中呢（参数怎么传）
    def onPause(self):
        """策略暂停"""
        self._controller.pauseRequest(self._strategyId)

    def onQuit(self):
        """策略停止"""
        self._controller.quitRequest(self._strategyId)

    def onResume(self):
        """策略运行"""
        self._controller.resumeRequest(self._strategyId)

    def onDelete(self):
        """删除策略"""
        self._controller.delStrategy(self._strategyId)