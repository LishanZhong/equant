import tkinter as tk
from utils.utils import rgb_to_hex
from .view import QuantApplication


# ParentCanvas
class CanvasFrame(tk.Canvas):
    def __init__(self, master):
        tk.Canvas.__init__(self, master)
        # highlightthickness: get rid of the light grey border of the canvas widgets
        self.config(width=34, height=36, bd=0, bg=rgb_to_hex(64, 20, 107), highlightthickness=0)
        self.pack(side=tk.RIGHT, expand=tk.NO, padx=1)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, event):
        self.config(bg=rgb_to_hex(84, 26, 131))

    def on_leave(self, event):
        self.config(bg=rgb_to_hex(64, 20, 107))


class MinimizeCanvas(CanvasFrame):
    def __init__(self, master):
        CanvasFrame.__init__(self, master)
        self.create_widgets()
        self.bind("<ButtonRelease-1>", self.on_minimize)

    def create_widgets(self):
        self.create_line(10, 20, 25, 20, width=2, fill='white')

    def on_minimize(self, event):
        # 判断鼠标是否离开
        self.master.master.master.state("iconic")


class MixedCancas(CanvasFrame):
    def __init__(self, master):
        CanvasFrame.__init__(self, master)
        self.create_max_widgets()
        self.bind("<ButtonRelease-1>", self.on_click)
        self.flag = True

    def create_max_widgets(self):
        self.create_line(10, 14, 27, 14, width=2, fill='white', tags="max")  # 如果27改为26的话，则线和矩阵的右边对不齐
        self.create_rectangle(10, 14, 26, 24, fill=rgb_to_hex(64, 20, 107), outline='white', tags="max")

    def create_min_widgets(self):
        self.create_line(13, 13, 25, 13, fill="white", smooth=True, tags="min")
        self.create_rectangle(13, 14, 24, 22, fill=rgb_to_hex(64, 20, 107), outline='white', tags="min")
        self.create_line(9, 16, 21, 16, fill="white", smooth=True, tags="min")
        self.create_rectangle(9, 17, 20, 25, fill=rgb_to_hex(64, 20, 107), outline='white', tags="min")

    def on_maximize(self):
        self.master.master.state("zoomed")
        # self.geometry("%dx%d+0+0"%(self.winfo_screenwidth(), self.winfo_screenheight()))

    def on_normal(self):
        self.master.master.state("normal")

    def on_click(self, event):
        print("haha")
        if self.flag:
            self.delete("max")
            self.flag = not self.flag
            self.create_min_widgets()
            self.on_maximize()

        else:
            self.delete("min")
            self.create_max_widgets()
            self.flag = not self.flag
            self.on_normal()


class CloseCanvas(CanvasFrame):
    def __init__(self, master):
        CanvasFrame.__init__(self, master)
        self.create_widgets()
        self.bind('<Enter>', self.on_enter)
        self.bind('<ButtonRelease-1>', self.on_close)

    def on_enter(self, event):
        self.config(bg='red')

    def on_close(self, event):
        # TODO: need a tip information
        self.master.master.master.destroy()

    def create_widgets(self):
        # TODO: cross line not aligned
        self.create_line(12, 14, 23, 25, width=2, fill="white", smooth=True)
        self.create_line(12, 25, 23, 14, width=2, fill="white", smooth=True)


class NormalCanvas(CanvasFrame):
    def __init__(self, master):
        CanvasFrame.__init__(self, master)
        self.create_widgets()
        self.bind("<ButtonRelease-1>", self.on_normal)

    def on_normal(self, event):
        self.master.master.state("normal")

    def create_widgets(self):
        self.create_line(13, 13, 25, 13, fill="white", smooth=True)
        self.create_rectangle(13, 14, 24, 22, fill=rgb_to_hex(64, 20, 107), outline='white')
        self.create_line(9, 16, 21, 16, fill="white", smooth=True)
        self.create_rectangle(9, 17, 20, 25, fill=rgb_to_hex(64, 20, 107), outline='white')


# parent window for displaying the app icon in taskbar
class ViewRoot(tk.Tk):

    def __init__(self, control):
        tk.Tk.__init__(self)
        self.control = control
        self.attributes('-alpha', 0.0)
        self.top = QuantMain(self, control)
        self.bind("<Unmap>", self.onRootIconify)
        self.bind("<Map>", self.onRootDeiconify)
        # 图标
        self.iconbitmap(bitmap=r"./icon/epolestar ix1.ico")
        self.top_state = None

    def get_top_handler(self):
        return self.top

    def run_(self):
        # window = tk.Frame(master=self.top)

        self.top.deiconify()
        self.top.mainloop()

    def onRootIconify(self, event):
        self.top_state = self.top.state()
        self.top.withdraw()

    def onRootDeiconify(self, event):
        # self.top.deiconify()
        self.top.state(self.top_state)
        self.top.deiconify()


class QuantMain(tk.Toplevel):
    def __init__(self, master, control):
        tk.Toplevel.__init__(self, master)
        self.control = control
        self.master = master
        self.overrideredirect(1)
        # self.attributes('-topmost', 1)   # window in front(no need)
        # set the Quant window's size and location
        width = self.master.winfo_screenwidth()*0.8
        height = self.master.winfo_screenheight()*0.8
        self.geometry('%dx%d+%d+%d' % (width, height, width*0.1, height*0.1))
        self.config(background=rgb_to_hex(64, 20, 107))
        self.create_widget()

    def create_widget(self):
        # make a frame for the title bar
        self.title_bar = tk.Frame(self, height=40, bg=rgb_to_hex(64, 20, 107), relief='flat', bd=0)

        # title name
        self.title_name = tk.Label(self.title_bar, text="极星量化", width=12, bg=rgb_to_hex(64, 20, 107),
                                   relief='flat', fg=rgb_to_hex(255, 255, 255), font=("微软雅黑", "-14", 'normal'),
                                   anchor=tk.CENTER, padx=-16)
        self.title_name.pack(side=tk.LEFT, expand=tk.NO)

        # put the close, maximize and minimize button on the title bar
        close_button = CloseCanvas(self.title_bar)
        mixed_button = MixedCancas(self.title_bar)
        minimize_button = MinimizeCanvas(self.title_bar)

        # bind event
        self.title_bar.bind('<B1-Motion>', self.move_window)

        # a canvas for the main area of the window
        window = tk.Canvas(self, bg=rgb_to_hex(227, 230, 233))

        # pack the widgets
        self.title_bar.pack(side=tk.TOP, fill=tk.X, expand=tk.NO)

        window.pack(padx=2, pady=2, side=tk.TOP, expand=1, fill=tk.BOTH)

        # Quant window
        self.quant_app = QuantApplication(window, self.control)
        self.quant_app.create_window()

    def move_window(self, event):
        # TODO: There is a bug!!
        def get_pos(event):
            xwin = self.winfo_x()
            ywin = self.winfo_y()
            startx = event.x_root
            starty = event.y_root

            ywin = ywin - starty
            xwin = xwin - startx

            def move_window(event):
                self.geometry('+{0}+{1}'.format(event.x_root + xwin, event.y_root + ywin))

            self.title_bar.bind('<B1-Motion>', move_window)

        self.title_bar.bind('<Button-1>', get_pos)

    def get_quant_handler(self):
        return self.quant_app