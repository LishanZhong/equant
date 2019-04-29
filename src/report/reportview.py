import os

import pandas as pd
import matplotlib
matplotlib.use('TkAgg')

import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.pyplot as plt, matplotlib.dates as mdate
from matplotlib import ticker
from datetime import datetime

import tkinter as tk
import tkinter.ttk as ttk
import time

from capi.com_types import *
from report.handler import EventHandler
from report.rightclickmenu import RightClickMenu
from utils.utils import int2date

# 设置中文显示
matplotlib.rcParams['font.sans-serif'] = ['FangSong']
matplotlib.rcParams['axes.unicode_minus'] = False


# report_item没有用
report_item = ["测试天数", "测试周期数", "信号消失次数", "初始资金", "最终权益",
               "空仓周期数", "最长连续空仓周期", "最长交易周期", "标准离差",
               "标准离差率", "夏普比率", "盈亏总平均/亏损平均", "权益最大回撤",
               "权益最大回撤时间", "权益最大回撤比", "权益最大回撤比时间"]

plt.style.use('ggplot')


class ReportView(tk.Frame):

    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.data = data
        self.config(width=800, height=500)
        self.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)
        self.make_widgets()

    def make_widgets(self):
        self.dir = Directory(self.data, self)
        self.dir.create_directory()
        # Detail(self.data, self)

    # def show(self):
    #     self.data['_report'].update()
    #     self.data['_report'].deiconify()


class Directory(tk.Frame):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.data = data
        self.parent = parent
        self.config(width=200, height=500)
        self.pack(side=tk.LEFT, fill=tk.Y)
        self.pack_propagate(0)
        self.make_widgets()
        self.detail_frame = Detail(self.data, self.parent)

    def make_widgets(self):
        self.data_tree = ttk.Treeview(self, height=30, selectmode="browse", show=['tree'])  # 树状
        self.menu = RightClickMenu(self.data_tree)

        self.data_tree.column('#0', stretch=False, width=200)  # width应该根据显示文字的长度进行变化
        self.ysb = tk.Scrollbar(self.data_tree, orient='vertical')
        self.xsb = tk.Scrollbar(self.data_tree, orient='horizontal')

        self.data_tree.config(yscrollcommand=self.ysb.set)
        self.data_tree.config(xscrollcommand=self.xsb.set)
        self.ysb.config(width=16, command=self.data_tree.yview)
        self.xsb.config(width=16, command=self.data_tree.xview)

        self.ysb.pack(side=tk.RIGHT, fill=tk.Y)
        self.xsb.pack(side=tk.BOTTOM, fill=tk.X)
        self.data_tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.data_tree.bind('<Button-3>', self.right_click_callback)
        self.data_tree.bind('<Double-1>', self.select_callback)
        self.data_tree.bind('<FocusOut>', self.focus_out_event)
        # self.data_tree.bind('<FocusIn>', self.focus_in_event)

    def create_directory(self):
        '''
        该处是动态生成数据树目录，需要获取到策略运行的一些信息
        :param parent: 父节点
        :return: None
        '''
        file_path = os.path.abspath("./reportdata")

        children = self.data_tree.get_children()
        for child in children:
            self.data_tree.delete(child)

        self.insert_child(file_path)

    def insert_child(self, path, parent=""):
        for file in os.listdir(path):  # 遍历当前目录
            if file != "__pycache__":  # 是不是需要判断文件是否存在
                file_path = os.path.join(path, file)
                values_path = file_path

                # windows下，此处TreeView有一个bug, len(valaues)==1时， 空格会被拆分成两个值，\\会消失
                oid = self.data_tree.insert(parent, 'end', text=file, values=[values_path, "!@#$%^&*"])
                self.data_tree.column('#0', stretch=False, width=300)
                if os.path.isdir(file_path):
                    self.insert_child(file_path, oid)

    def select_callback(self, event):
        '''
        树控件的点击回调事件
        :param event: 事件类
        :return: None
        '''
        select = event.widget.selection()  # 获取所选的项（可能是多项，所以要for循环）
        for idx in select:
            if self.data_tree.parent(idx):
                report_name = self.data_tree.item(idx)['text']
                directory_id = self.data_tree.parent(idx)
                directory_name = self.data_tree.item(directory_id)['text']
                if self.data_tree.item(idx)['text'] == report_name:
                    data = self.parse_data(directory_name, report_name)
                    self.show(data)

    def show(self, data):
        self.detail_frame.fund.display(data)
        self.detail_frame.analyse.display(data)
        self.detail_frame.stage_statis.display(data)
        self.detail_frame.trade.display(data)
        self.detail_frame.graph.set_initial_graph(data)

    def right_click_callback(self, event):
        select = self.data_tree.identify_row(event.y)
        if select:
            self.data_tree.focus(select)
            self.data_tree.selection_set(select)
            # self.focus_set()
            self.menu.popupmenu(event)
            # self.data_tree.selection_toggle(select)
            self.update_idletasks()
            # self.data_tree.selection_remove(select)

    def focus_out_event(self, event):
        _item = self.data_tree.focus()
        self.data_tree.selection_remove(_item)
        # self.data_tree.selection_toggle(_item)

    def focus_in_event(self, event):
        _item = self.data_tree.focus()
        self.data_tree.selection_set(_item)

    @staticmethod
    def parse_data(directory, file_name):
        # 根据目录树的点击事件，解析对应的数据
        import os
        import pickle

        path = os.path.abspath(r"./reportdata/")
        for file in os.listdir(path):
            if file == directory:
                file_path = os.path.join(path, directory)
                for f in os.listdir(file_path):
                    if f == file_name:
                        _file = os.path.join(file_path, f)
                        with open(_file, 'rb') as f_:
                            data = pickle.load(f_)
                            return data

        return None


class BaseFrame(tk.Frame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config(width=600, height=500)
        self.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)
        # ttk.Style().configure("TNotebook", font=('楷体', 12))

    @staticmethod
    def create_widgets(figure, parent):
        '''
        display the figure in tkinter
        :param figure: which figure to display in tkinter window
        :param parent: the parent Window of figure displayed
        :return: None
        '''
        canvas = FigureCanvasTkAgg(figure, parent)
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)
        # canvas.draw()

        toolbar = NavigationToolbar2Tk(canvas, parent)
        toolbar.update()
        canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)


class Detail(BaseFrame):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.data = data
        self.make_widgets()
        # ttk.Style函数不会用，怎么设置的呢？？？
        self.style = ttk.Style(self.master)
        self.style.configure("TNotebook", padding=2)
        # self.style.configure("TNotebook.Tab", font=('楷体', 12))

    def make_widgets(self):
        tab_strip = ttk.Notebook(self)
        tab_strip.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # text = ['资金曲线', '分析报告', '阶段总结', '交易详情', '图表分析']
        self.fund         = Fund(tab_strip)
        self.analyse      = Analyse(tab_strip)
        self.stage_statis = StageStatis(tab_strip)
        self.trade        = Trade(tab_strip)
        self.graph        = Graph(self.data, tab_strip)

        self.fund.display(self.data)
        self.fund.pack(fill=tk.BOTH, expand=True)
        tab_strip.add(self.fund, padding=5, text='资金曲线')

        self.analyse.display(self.data)
        self.analyse.pack(fill=tk.BOTH, expand=True)
        tab_strip.add(self.analyse, padding=5, text='分析报告')

        self.stage_statis.display(self.data)
        self.stage_statis.pack(fill=tk.BOTH, expand=True)
        tab_strip.add(self.stage_statis, padding=5, text='阶段总结')

        self.trade.display(self.data)
        self.trade.pack(fill=tk.BOTH, expand=True)
        tab_strip.add(self.trade, padding=5, text='交易详情')

        self.graph.set_initial_graph(self.data)
        self.graph.pack(fill=tk.BOTH, expand=True)
        tab_strip.add(self.graph, padding=5, text='图表分析')


class Fund(BaseFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 设置光标样式
        # self.config(cursor='sb_h_double_arrow')
        self.make_widgets()
        self.handle = EventHandler(self.fig, self.canvas, self.ax)
        self.handle.connect()

    def make_widgets(self):
        self.fig, self.ax = plt.subplots()
        self.ax.yaxis.grid(False, linestyle="-.", color='silver')
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        # self.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)

    def display(self, data):
        self.ax.cla()
        # self.ax.clear()
        # 根据回测日期选择显示的时间格式fmt
        # temp = [f['Time'] for f in data["Fund"]]
        x = [pd.Timestamp(int2date(f['Time'])) for f in data['Fund']]
        y = [f['DynamicEquity'] for f in data['Fund']]
        self.ax.set_xlim(0, len(y)-1)
        self.handle.set_border()
        self.handle.set_x_labels(x)
        if data['KLineType'] == EEQU_KLINE_DAY:
            fmt = mdate.DateFormatter('%Y-%m')
        elif data['KLineType'] == EEQU_KLINE_MINUTE:
            fmt = mdate.DateFormatter('%Y-%m-%d')
        else:  # 有待更改
            fmt = mdate.DateFormatter('%Y-%m-%d')
        self.ax.plot(y, marker='.', color='red', linewidth=2.0, linestyle='-')
        self.ax.set_xticklabels(x)

        def format_date(x_, pos=None):
            if x_ < 0 or x_ > len(x) - 1:
                return
            return x[int(x_)]

        #TODO: length先暂时这样处理吧！
        length = 0
        if len(x) > 0 and len(x) <= 100:
            length=30
        elif len(x) > 100 and len(x) <= 1000:
            length = 200
        elif len(x) >1000 and len(x) < 10000:
            length = 2000
        else:
            length = 20000


        self.ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))
        self.ax.xaxis.set_major_locator(ticker.MultipleLocator(length))
        # 此处使用self.canvas.draw()会使程序崩溃
        self.canvas.draw_idle()


class Analyse(BaseFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.make_report()

    def make_report(self):
        self.tree = ttk.Treeview(self, show=[], columns=('a', 'b', 'c', 'd'))
        vbar = tk.Scrollbar(self, orient='vertical')
        self.tree.column('a', width=250, anchor=tk.W)
        self.tree.column('b', width=300, anchor=tk.W)

        vbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.tree.config(yscrollcommand=vbar.set)
        vbar.config(width=16, command=self.tree.yview)
        self.tree.bind('<FocusOut>', self.focus_out_event)
        # self.tree.bind('<FocusIn>', self.focus_in_event)

    def display(self, data):
        # 这里放要展示的数据
        children = self.tree.get_children()
        for child in children:
            self.tree.delete(child)
        text = (
            '资金', '合约信息', '周期', '计算开始时间', '计算结束时间', '测试天数', '最终权益', '空仓周期数',
            '最长连续空仓周期', '最长交易周期', '标准离差', '标准离差率', '夏普比率',
            '盈亏总平均/亏损平均', '权益最大回撤',   '权益最大回撤时间', '权益最大回撤比', '权益最大回测比时间',
            '风险率', '收益率/风险率', '盈利率', '实际盈利率', '年化单利收益率', '月化单利收益率', '年化复利收益率',
            '月化复利收益率', '胜率', '平均盈利/平均亏损', '平均盈利率/平均亏损率', '净利润', '总盈利',
            '总亏损', '总盈利/总亏损', '其中持仓浮盈', '交易次数', '盈利比率', '盈利次数', '亏损次数', '持平次数',
            '平均盈亏', '平均盈利', '平均亏损', '盈利持续最大天数', '盈利持续最大天数出现时间', '亏损持续最大天数',
            '亏损持续最大天数出现时间', '盈利环比增加持续最大天数', '盈利环比增加持续最大天数出现时间',
            '亏损环比增加持续最大天数', '亏损环比增加持续最大天数出现时间',
            '期间最大权益', '期间最小权益', '手续费', '滑点损耗', '成交额'
        )

        detail = data['Detail']
        detailFormatter = [
            '{:.2f}'.format(float(detail["InitialFund"])),
            detail["Contract"],
            detail["Period"],
            detail["StartTime"],
            detail["EndTime"],
            detail["TestDay"],
            '{:.2f}'.format(float(detail["FinalEquity"])),
            detail["EmptyPeriod"],
            detail["MaxContinueEmpty"],
            detail["MaxTradePeriod"],
            '{:.2f}'.format(float(detail["StdDev"])),
            detail["StdDevRate"] if isinstance(detail["StdDevRate"], str) else '{:.2f}'.format(float(detail["StdDevRate"])),
            '{:.2f}'.format(float(detail["Sharpe"])),
            '{:.2f}'.format(float(detail["PlmLm"])) if isinstance(detail["PlmLm"], float) else detail["PlmLm"],
            '{:.2f}'.format(float(detail["MaxRetrace"])),
            detail["MaxRetraceTime"],
            '{:.2f}'.format(float(detail["MaxRetraceRate"])),
            detail["MaxRetraceRateTime"],
            '{:.2f}'.format(float(detail["Risky"])),
            '{:.2f}'.format(float(detail["RateofReturnRisk"]))\
                if isinstance(detail["RateofReturnRisk"], float) else detail["RateofReturnRisk"],
            '{:.2f}'.format(float(detail["Returns"])),
            '{:.2f}'.format(float(detail["RealReturns"])),
            '{:.2f}'.format(float(detail["AnnualizedSimple"])),
            '{:.2f}'.format(float(detail["MonthlySimple"])),
            '{:.2f}'.format(float(detail["AnnualizedCompound"]))\
                if isinstance(detail["AnnualizedCompound"], float) else detail["AnnualizedCompound"],
            '{:.2f}'.format(float(detail["MonthlyCompound"]))\
                if isinstance(detail["MonthlyCompound"], float) else detail["MonthlyCompound"],
            '{:.2f}'.format(float(detail["WinRate"])) if isinstance(detail["WinRate"], float) else detail["WinRate"],
            '{:.2f}'.format(float(detail["MeanWinLose"]))\
                if isinstance(detail["MeanWinLose"], float) else detail["MeanWinLose"],
            '{:.2f}'.format(float(detail["MeanWinLoseRate"]))\
                if isinstance(detail["MeanWinLoseRate"], float) else detail["MeanWinLoseRate"],
            '{:.2f}'.format(float(detail["NetProfit"]))\
                if isinstance(detail["NetProfit"], float) else detail["NetProfit"],
            '{:.2f}'.format(float(detail["TotalWin"])),
            '{:.2f}'.format(float(detail["TotalLose"])),
            '{:.2f}'.format(float(detail["RatioofWinLose"]))\
                if isinstance(detail["RatioofWinLose"], float) else detail["RatioofWinLose"],
            '{:.2f}'.format(float(detail["HoldProfit"])),
            detail["TradeTimes"],
            '{:.2f}'.format(float(detail["WinPercentage"])),
            detail["WinTimes"],
            detail["LoseTimes"],
            detail["EventTimes"],
            '{:.2f}'.format(float(detail["MeanProfit"])),
            '{:.2f}'.format(float(detail["MeanWin"])),
            '{:.2f}'.format(float(detail["MeanLose"])),
            detail["MaxWinContinueDays"],
            detail["MaxWinContinueDaysTime"],
            detail["MaxLoseContinueDays"],
            detail["MaxLoseContinueDaysTime"],
            detail["MaxWinComparedIncreaseContinueDays"],
            detail["MaxWinComparedIncreaseContinueDaysTime"],
            detail["MaxLoseComparedIncreaseContinueDays"],
            detail["MaxLoseComparedIncreaseContinueDaysTime"],
            '{:.2f}'.format(float(detail["MaxEquity"])),
            '{:.2f}'.format(float(detail["MinEquity"])),
            '{:.2f}'.format(float(detail["Cost"])),
            '{:.2f}'.format(float(detail["SlippageCost"])),
            '{:.2f}'.format(float(detail["Turnover"])),
        ]
        for t, value in zip(text, detailFormatter):
            # self.tree.insert('', 'end', values=(t, detail[value]))
            self.tree.insert('', 'end', values=(t, value))

    def focus_out_event(self, event):
        _item = self.tree.focus()
        self.update_idletasks()
        self.tree.selection_remove(_item)

    def focus_in_event(self, event):
        _item = self.tree.focus()
        self.focus_set()
        self.tree.selection_set(_item)


class StageStatis(BaseFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.create_graph_widgets()
        self.make_widgets()

    def create_graph_widgets(self):
        """创建五个treeview控件"""
        column = ('a', 'b', 'c', 'd', 'e', 'f', 'g')

        self.y_form = ttk.Treeview(self, columns=column, selectmode="none", show=["headings"])
        self.q_form = ttk.Treeview(self, columns=column, selectmode="none", show=["headings"])
        self.m_form = ttk.Treeview(self, columns=column, selectmode="none", show=["headings"])
        self.w_form = ttk.Treeview(self, columns=column, selectmode="none", show=["headings"])
        self.d_form = ttk.Treeview(self, columns=column, selectmode="none", show=["headings"])

    def make_widgets(self):
        column = ('a', 'b', 'c', 'd', 'e', 'f', 'g')
        heading = ('日期', '权益', '净利润', '盈利率', '胜率', '平均盈利/亏损', '净利润增长速度')
        title = ('年度分析', '季度分析', '月度分析', '周分析', '日分析')
        labelfont = ('楷体', 12, 'bold')
        self.create_graph_widgets()
        graph = (self.y_form, self.q_form, self.m_form, self.w_form, self.d_form)

        # 折叠窗口功能，目前没有实现
        # row = 0
        # for t, g in zip(title, graph):
        #     pady = 0 if row % 2 == 0 else 5
        #     self.create_statis_frame(row, t, g, pady)
        #     row += 1

        for t, g in zip(title, graph):
            label = tk.Label(self, text=t, bg='navy', fg='yellow', font=labelfont, width=116, height=1)
            label.pack(side=tk.TOP, fill=tk.X, pady=10)
            label.bind("<Button-1>", self.on_one_left_click)
            vbar = tk.Scrollbar(g, orient='vertical')
            vbar.config(command=g.yview)
            g.config(yscrollcommand=vbar.set)
            g.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)
            vbar.pack(side=tk.RIGHT, fill=tk.Y)
            for c, head in zip(column, heading):
                g.column(c, width=20, anchor="center")
                g.heading(c, text=head)

    def display(self, data):
        # 这里放要展示的数据
        # 以下三个都是树根
        graph = (self.y_form, self.q_form, self.m_form, self.w_form, self.d_form)
        stage_data = data['Stage']
        for g, sd in zip(graph, stage_data.values()):
            # ------------------------------------
            children = g.get_children()
            for child in children:
                g.delete(child)
            # -------------------------------------
            for d in sd: #  int2date(d['Time']).strftime('%Y%m%d')
                g.insert('', 'end', values=(d['Time'],
                                            '{:.2f}'.format(float(d['Equity'])),
                                            '{:.2f}'.format(float(d['NetProfit'])),
                                            '{:.2%}'.format(float(d['Returns'])),
                                            '{:.2%}'.format(float(d['WinRate'])),
                                            '{:.2f}'.format(float(d['MeanReturns'])),
                                            '{:.2%}'.format(float(d['IncSpeed']))))

    def on_one_left_click(self, event, widget):
        #print("tell you!")
        widget.pack_forget()

    def create_statis_frame(self, row, label_text, tree, space):
        """

        :param row: 第几行
        :param label_text:label需要显示的文本
        :param tree: 好像没有用
        :param space: 间距
        :return:
        """
        # labelfont = 'bold'
        column = ('a', 'b', 'c', 'd', 'e', 'f', 'g')
        heading = ('日期', '权益', '净利润', '盈利率', '胜率', '平均盈利/亏损', '净利润增长速度')

        f = tk.Frame(self)
        row = tk.Frame(f)
        f.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES, pady=space)
        row.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)
        L1 = tk.Label(row, text=label_text, bg='navy', fg='yellow', width=106)
        L1.pack(side=tk.LEFT, fill=tk.X, expand=tk.YES)
        L2 = tk.Label(row, text=' @ ', bg='navy', fg='yellow')
        L2.pack(side=tk.LEFT, fill=tk.X)

        tree = ttk.Treeview(f, columns=column, selectmode="none", show=["headings"])
        vbar = tk.Scrollbar(tree, orient='vertical')
        vbar.config(command=tree.yview)
        tree.config(yscrollcommand=vbar.set)
        tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        vbar.pack(side=tk.RIGHT, fill=tk.Y)

        L2.bind("<Button-1>", func=self.handler_adaptor(self.on_one_left_click, widget=tree))
        for c, head in zip(column, heading):
            tree.column(c, width=20, anchor="center")
            tree.heading(c, text=head)

    def handler_adaptor(self, fun, **kwds):
        """事件处理函数适配器"""
        return lambda event, fun=fun, kwds=kwds: fun(event, **kwds)


class Trade(BaseFrame):
    '''
    StageStatis类生成测试报告界面上阶段总结
    '''
    def __init__(self, parent=None):
        super().__init__(parent)
        self.make_widgets()

    def make_widgets(self):
        column = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k')
        self.tree = ttk.Treeview(self, columns=column, selectmode="browse", show=["headings"])
        # width应该根据窗口的的大小进行变化，不能是一个固定值
        self.tree.column('#0', stretch=False, width=800)
        vbar = tk.Scrollbar(self, orient='vertical')

        self.tree.config(yscrollcommand=vbar.set)
        vbar.config(command=self.tree.yview)

        vbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        heading = ('时间', '合约', '交易类型', '下单类型', '成交数量', '成交价', '成交额', '委托数量', '平仓盈亏', '手续费', '滑点损耗')
        for c, h in zip(column, heading):
            self.tree.column(c,  width=80, anchor=tk.W)
            self.tree.heading(c, text=h)

        self.tree.bind('<FocusOut>', self.focus_out_event)
        self.tree.bind('<FocusIn>', self.focus_in_event)

    def display(self, data):
        # 这里放要展示的数据
        children = self.tree.get_children()
        for child in children:
            self.tree.delete(child)
        orders = data['Orders']
        kline_type = data['KLineType']
        for eo in orders:
            time = self.get_order_time(kline_type, eo['Order'])
            trade_type = self.get_trade_type(eo['Order'])
            self.tree.insert('', 'end', values=(time,
                                                eo['Order']['Cont'],
                                                trade_type,
                                                '市价单',
                                                eo['Order']['OrderQty'],
                                                '{:.1f}'.format(float(eo['Order']['OrderPrice'])),
                                                '{:.1f}'.format(float(eo['Turnover'])),
                                                eo['Order']['OrderQty'],
                                                '{:.1f}'.format(float(eo['LiquidateProfit'])),
                                                '{:.1f}'.format(float(eo['Cost'])),
                                                '{:.1f}'.format(0)
                                                )
                            )

    def get_order_time(self, kline_type, order):
        t = str(order['DateTimeStamp'])
        # TODO:kline_type传进来了一个字典["KLineType": , "KLineSlice": ]
        if kline_type["KLineType"] == EEQU_KLINE_DAY:
            # time = t[0:4] + "年" + t[4:6] + "月" + t[6:8] + "日"
            time = t[0:8]

        elif kline_type["KLineType"] == EEQU_KLINE_MINUTE:
            time = t[0:8] + " " + " " + t[8:10] + ":" + t[10:12] + ":" + t[12:14]

        elif kline_type["KLineType"] == EEQU_KLINE_TICK:
            time = t[0:8] + " " + t[8:10] + ":" + t[10:12] + ":" + t[12:14] + '.' + t[-3:]

        return time

    def get_trade_type(self, order):
        direct = order['Direct']
        offset = order['Offset']
        if direct == dBuy:
            if offset == oNone:
                trade_type = "买"
            elif offset == oOpen:
                trade_type = "买开"
            elif offset == oCover:
                trade_type = "买平"
            elif offset == oCoverT:
                trade_type = "买平今"
            elif offset == oOpenCover:
                trade_type = "买开平"
            elif offset == oCoverOpen:
                trade_type = "买平开"
        elif direct == dSell:
            if offset == oNone:
                trade_type = "卖"
            elif offset == oOpen:
                trade_type = "卖开"
            elif offset == oCover:
                trade_type = "卖平"
            elif offset == oCoverT:
                trade_type = "卖平今"
            elif offset == oOpenCover:
                trade_type = "卖开平"
            elif offset == oCoverOpen:
                trade_type = "卖平开"
        return trade_type

    def focus_out_event(self, event):
        _item = self.tree.focus()
        self.tree.selection_remove(_item)

    def focus_in_event(self, event):
        _item = self.tree.focus()
        self.tree.selection_set(_item)


class Graph(BaseFrame):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.data = data
        self.make_widgets()
        #TODO: 图表分析的事件处理有错误，先不绑定
        # self.handler = EventHandler(self.fig, self.canvas, self.ax)
        # self.handler.connect()

    def make_widgets(self):
        graph_catalog = {
            "年度分析": ["年度权益", "年度净利润", "年度盈利率", "年度胜率", "年度平均盈亏", "年度权益增长"],
            "季度分析": ["季度权益", "季度净利润", "季度盈利率", "季度胜率", "季度平均盈亏", "季度权益增长"],
            "月度分析": ["月度权益", "月度净利润", "月度盈利率", "月度胜率", "月度平均盈亏", "月度权益增长"],
            "周分析": ["周权益",   "周净利润",   "周盈利率",   "周胜率",   "周平均盈亏",   "周权益增长"],
            "日分析": ["日权益",   "日净利润",   "日盈利率",   "日胜率",   "日平均盈亏",   "日权益增长"]
        }

        self.fig, self.ax = plt.subplots(figsize=(6, 6))
        self.graph_frame = tk.Frame(self, height=800)
        self.graph_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=tk.YES)
        self.canvas = FigureCanvasTkAgg(self.fig, self.graph_frame)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)
        self.tree_frame = tk.Frame(self, width=200, height=800)
        self.tree_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.graph_tree = ttk.Treeview(self.tree_frame,  selectmode="browse", show="tree")
        self.graph_tree.column('#0', stretch=False, width=200)
        vbar = tk.Scrollbar(self.tree_frame, orient='vertical')

        self.graph_tree.config(yscrollcommand=vbar.set)
        vbar.config(command=self.graph_tree.yview)

        vbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.graph_tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        parent_node = ['年度分析', '季度分析', '月度分析', '周分析', '日分析']
        for p, (key, value) in zip(parent_node, graph_catalog.items()):
            open = True if p == '年度分析' else False
            tr = self.graph_tree.insert("", 'end', text=key,  tags=p, open=open)
            keys = ['Equity', 'NetProfit', 'Returns', 'WinRate', 'MeanReturns', 'IncSpeed']
            for k, v in zip(keys, value):
                self.graph_tree.insert(tr, 'end', text=v, tags=k, open=False)

            # 设置初始选中条目
            children = self.graph_tree.get_children(tr)
            for child in children:
                if self.graph_tree.item(child)["text"] == "年度权益":
                    self.graph_tree.selection_set(child)

        self.graph_tree.bind('<<TreeviewSelect>>', self.select_callback)
        self.tree_frame.bind('<FocusOut>', self.focus_out_event)
        self.tree_frame.bind('<FocusIn>', self.focus_in_event)
        self.graph_tree.pack()

    def focus_out_event(self, event):
        _item = self.graph_tree.focus()
        self.graph_tree.selection_toggle(_item)

    def focus_in_event(self, event):
        _item = self.graph_tree.focus()
        self.graph_tree.selection_set(_item)

    def set_initial_graph(self, data):
        # 初始时选中第一个怎么选中，还不知道
        self.data = data
        self.ax.cla()
        self.ax.clear()
        x, y = self.get_plot_data('年度分析', 'Equity')
        self.ax.xaxis.grid(False, linestyle="-.", color="silver")
        self.ax.yaxis.grid(False, linestyle="-.", color="silver")
        self.ax.bar(range(len(y)), y)
        self.ax.set_title('Equity')
        self.ax.set_xlabel("a")
        self.ax.set_ylabel("b")
        self.canvas.draw_idle()

    def get_plot_data(self, key, tag):
        x, y = [], []
        for sd in self.data['Stage'][key]:
            x.append(sd.get('Time'))
            y.append(sd.get(tag))
        return x, y

    def select_callback(self, event):
        '''
        树控件的点击回调事件
        :param event: 事件类
        :return: None
        '''
        x_title = ['年份', '季', '月份', '周', '日']
        y_title = ['权益', '净利润', '盈利率', '胜率', '平均盈亏', '权益增长速度']
        select = event.widget.selection()
        for id in select:
            if self.graph_tree.parent(id):
                parent_id = self.graph_tree.parent(id)
                children_item = self.graph_tree.item(id)["text"]
                children_tag = self.graph_tree.item(id)["tags"][0]
                parent_tag = self.graph_tree.item(parent_id)["tags"][0]
                print("parent_id", parent_id)
                print("children_item", children_item)
                print("children_tag", children_tag)
                print("parent_tag", parent_tag)

                x, y = self.get_plot_data(parent_tag, children_tag)
                self.ax.cla()
                self.ax.clear()

                self.ax.xaxis.grid(False, linestyle="-.", color="silver")
                self.ax.yaxis.grid(False, linestyle="-.", color="silver")
                self.ax.bar(range(len(y)), y)
                self.ax.set_title(children_item)
                self.ax.set_xlabel("a")
                self.ax.set_ylabel("b")
                self.canvas.draw()


if __name__ == '__main__':
    config = [1, 2, 3, 4, 5]
    Detail(config)
