import os
from tkinter import *
from tkinter import ttk, messagebox, Frame
from utils.utils import *
from .language import Language
from .editor import ScrolledText
from .com_view import QuantFrame, QuantToplevel
from api.api_func import _all_func_
from api.base_api import BaseApi
from .editor import HelpText



class QuantHelperHead(object):
    def __init__(self, frame, control, language):
        self.control = control
        self.language = language
        
        self.head_frame = Frame(frame, bg=rgb_to_hex(245, 245, 245), height=30)
        Label(self.head_frame, bg=rgb_to_hex(245, 245, 245), text="函数列表").pack(side=LEFT)
        self.head_frame.pack(fill=X, ipady=1)

class QuantHelper(QuantFrame):
    def __init__(self, frame, control, language):
        self.control = control
        self.language = language
        self.root_frame = Frame(frame, height=frame['height'], width=frame['width'])
        self.root_frame.pack_propagate(0)
        self.root_frame.pack()
        
        self.root_tree = None
        
        self.api_dict = _all_func_
        
    def create_list(self):
        right_bar = ttk.Scrollbar(self.root_frame, orient="vertical")
        right_bar.pack(side=RIGHT, fill=Y)

        self.root_tree = ttk.Treeview(self.root_frame, show='tree', style="Filter.Treeview",
                                      columns=['name'], yscrollcommand=right_bar.set)
        #默认列表示函数名
        self.root_tree.column('0', anchor='w', stretch=True)
        #函数说明
        self.root_tree.column('name', anchor='w', stretch=True)
        self.insert_api()
        right_bar.config(command=self.root_tree.yview)
        self.root_tree.pack(fill=BOTH, expand=YES)
        self.root_frame.pack(fill=BOTH, expand=YES)
        
        #绑定事件
        self.root_tree.bind("<ButtonRelease-1>", self.item_click)
        
    def insert_api(self):
        for key, value in self.api_dict.items():
            root = self.root_tree.insert("", "end", open=False, text=key)
            for func in value:
                self.root_tree.insert(root, 'end', text=func[0], values=(func[1]))
                
    def item_click(self, event):
        select = event.widget.selection()
        for idx in select:
            text = self.root_tree.item(idx)['text']
            
            if text in self.api_dict:
                self.control.set_help_text(text, '')
            
            func = globals()['BaseApi'].__dict__.get(text, None)
            if not func: continue
            #检查注释
            if func.__doc__:
                self.control.set_help_text(text, func.__doc__)
            else:
                self.control.set_help_text(text, 'None')
        
        
class QuantHelperText(object):
    def __init__(self, frame, control,language):
        self.control = control
        self.language = language
        self.parent_frame = frame
        self.root_frame = Frame(frame, bg=rgb_to_hex(245, 245, 245), height=30)
        self.help_label = Label(self.root_frame, text="函数说明", bg=rgb_to_hex(245, 245, 245))
        self.help_label.pack(side=LEFT)
        self.root_frame.pack_propagate(0)
        self.root_frame.pack(fill=X)
        
        self.help_text = None
        
    def create_text(self):
        self.help_text = HelpText(self.parent_frame, bd=0)
        self.help_text.createScrollbar()
        self.help_text.pack(fill=BOTH, expand=YES)
        
    def insert_text(self, funcName, text):
        #更新函数说明
        self.help_label.config(text=funcName)
        #更新帮助说明
        if text:
            content = text.replace("    ", "")

            self.help_text.setText(content)
