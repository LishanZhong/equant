from tkinter import *
import tkinter.ttk as ttk

from utils.utils import rgb_to_hex


# ttk
# button:      "TButton"
# treeview:    "Treeview"
# label:       "TLabel"
# notebook:    "TNotebook"
# panedwindow: "TPanedwindow"
# tk
# frame
# text:
# canvas
# Scrollbar


# TitleBar: 颜色：64, 20, 107
# Frame: 颜色：227, 230, 233
# 字体颜色：51, 51， 51




def set_app_style():
    style = ttk.Style()
    style.theme_create("quant_style_one", parent="alt", settings={
        ".":                 {"configure": {"background":     "red",
                                            "foreground":     "blue",
                                            "relief":         "flat",
                                            "highlightcolor": "green"}},

        "TLabel":            {"configure": {"foreground":      "red",
                                            "padding":         "10",
                                            "font":            ("微软雅黑", 12)}},

        "TButton":           {"configure": {"font":            ("微软雅黑", 13, 'bold'),
                                            "background":      "black",
                                            "foreground":      "green"},
                              "map":       {"background":      [('pressed', '!disalbed', 'black'), ('active', 'white')],
                                            "foreground":      [('pressed', 'red'), ('active', 'blue')]}},

        "TNotebook":        {"configure":  {"padding":         5}},
        "TNotebook.Tab":    {"configure":  {"padding":         [20, 1],
                                            "foreground":      "white"},
                             "map":        {"background":      [("selected", "red")],
                                            "expand":          [("selected", [1, 1, 1, 0])]}},
        "Treeview":         {"configure":  {"foreground":      "red",
                                            "background":       "green"},
                             "map":         {}}
    })

    style.theme_use("quant_style_one")


# Treeview
style = ttk.Style(master=None)
style.theme_use('winnative')  # 主题在有些操作系统上可能不可用
style.configure("Filter.Treeview", foreground="##000000", background="#FEF9F4")
style.layout('Filter.Treeview', [
            ('Treeview.entry', {
                'border': '1', 'children':
                    [('Treeview.padding', {
                        'children':
                            [('Treeview.treearea', {'sticky': 'nswe'})], 'sticky': 'nswe'
                    })],
                'sticky': 'nswe'
            })
        ])

style.configure('Wild.TButton', background='blacl', foreground='white', highlightthickness='20', font=('Helvetica', 18, 'bold'))
style.map('Wild.TButton',
          foreground=[('disabled', 'yellow'),
                      ('pressed', 'red'),
                      ('active', 'blue')],
          background=[('disabled', 'magenta'),
                      ('pressed', '!focus', 'cyan'),
                      ('active', 'green')],
          highlightcolor=[('focus', 'green'),
                          ('!focus', 'red')],
          relief=[('pressed', 'groove'),
                  ('!pressed', 'ridge')])


