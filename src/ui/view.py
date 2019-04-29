from tkinter import *
from utils.utils import *
from .language import Language
from .editor_view import QuantEditor,QuantEditorHead
from .helper_view import QuantHelper,QuantHelperHead, QuantHelperText
from .monitor_view import QuantMonitor
from .com_view import LoadWin

from report.reportview import ReportView
from .com_view import HistoryToplevel


class QuantApplication(object):
    '''主界面'''
    def __init__(self, top, control):
        self.root = top
        self.control = control
        self.language = Language("EquantMainFrame")

        self.root.protocol("WM_DELETE_WINDOW", self.quantExit)

        #monitor_text需要跟日志绑定
        self.monitor_text = None
        self.editor_text_frame = None
        self.top_pane_left_up = None
        self.signal_text = None
        
        #窗口类
        self.quant_editor = None
        self.quant_helper = None
        self.quant_editor_head = None
        self.quant_helper_head = None
        self.quant_monitor = None
        self.loadWin = None  # 加载按钮弹出窗口

    def mainloop(self):
        self.root.mainloop()

    def create_window(self):
        #srceen size
        width = self.root.winfo_screenwidth()*0.8
        height = self.root.winfo_screenheight()*0.8
        
        #window location
        self.root.geometry('%dx%d+%d+%d' % (width, height, width*0.1, height*0.1))
        #title
        self.root.title("极星量化")
        self.root.iconbitmap(bitmap=r'./icon/epolestar ix1.ico')
        top_frame = Frame(self.root)
        top_frame.pack(fill=BOTH, expand=YES)

        # 创建主窗口,分为左右两个窗口，大小由子控件决定
        top_pane = PanedWindow(top_frame, orient=HORIZONTAL, sashrelief=GROOVE, sashwidth=1.5,
                               showhandle=False, opaqueresize=True)
        top_pane.pack(fill=BOTH, expand=YES)
        
        # 左窗口分上下窗口
        top_pane_left = PanedWindow(top_pane, orient=VERTICAL, sashrelief=GROOVE,
                                    sashwidth=1.5, opaqueresize=True, showhandle=False)
        # 右窗口，分上下窗口
        top_pane_right = PanedWindow(top_pane, orient=VERTICAL, sashrelief=GROOVE,
                                     sashwidth=1.5, opaqueresize=True, showhandle=False)

        top_pane.add(top_pane_left, stretch='always')
        top_pane.add(top_pane_right)
        

        # 左窗口分为上下两部分，右窗口分为上下两部分
        
        left_up_frame = Frame(top_pane_left, bg=rgb_to_hex(255, 255, 255), height=height*3/4, width=width*4/5)  # 左上
        left_down_frame = Frame(top_pane_left, bg=rgb_to_hex(255, 255, 255), height=height*1/4, width=width*4/5)  # 左下
        right_up_frame = Frame(top_pane_right, bg=rgb_to_hex(255, 255, 255), height=height*3/4, width=width*1/5)  # 右上
        right_down_frame = Frame(top_pane_right, bg=rgb_to_hex(255, 255, 255), height=height*1/4, width=width*1/5)  # 右下

        top_pane_left.add(left_up_frame, stretch='always')
        top_pane_left.add(left_down_frame, stretch='always')
        top_pane_right.add(right_up_frame, stretch='always')
        top_pane_right.add(right_down_frame, stretch='always')
        

        # 策略标题
        self.quant_editor_head = QuantEditorHead(left_up_frame, self.control,self.language)
        #策略树和编辑框
        self.quant_editor = QuantEditor(left_up_frame, self.control, self.language)
        #创建策略树
        self.quant_editor.create_tree()
        #创建策略编辑器
        self.quant_editor.create_editor()
        #api函数标题
        self.quant_helper_head = QuantHelperHead(right_up_frame, self.control, self.language)
        #系统函数列表
        self.quant_helper = QuantHelper(right_up_frame, self.control, self.language)
        self.quant_helper.create_list()
       
        #系统函数说明
        self.quant_helper_text = QuantHelperText(right_down_frame, self.control, self.language)
        self.quant_helper_text.create_text()
        
        # 监控窗口
        self.quant_monitor = QuantMonitor(left_down_frame, self.control, self.language)
        self.quant_monitor.createMonitor()
        # self.quant_monitor.create_execute()
        self.quant_monitor.createExecute()
        # self.create_monitor()
        self.quant_monitor.createSignal()
        self.quant_monitor.createErr()

    def updateLogText(self):
        self.quant_monitor.updateLogText()

    def updateSigText(self):
        self.quant_monitor.updateSigText()

    def updateErrText(self):
        self.quant_monitor.updateErrText()
        
    def set_help_text(self, funcName, text):
        self.quant_helper_text.insert_text(funcName, text)

    def updateStrategyTree(self, path):
        # self.quant_editor.update_all_tree()
        self.quant_editor.update_tree(path)

    def updateEditorHead(self, text):
        self.quant_editor.updateEditorHead(text)

    def updateEditorText(self, text):
        self.quant_editor.updateEditorText(text)

    # def updateExecuteList(self, executeList):
    #     self.quant_monitor.updateExecuteList(executeList)
        
    def updateSingleExecute(self, dataDict):
        self.quant_monitor.updateSingleExecute(dataDict)

    def createLoadWin(self):
        """弹出量化设置界面"""
        self.loadWin = LoadWin(self.control, self.root)
        self.loadWin.display()

    def setLoadState(self):
        self.quant_editor.setLoadBtnState()

    def quantExit(self):
        """量化界面关闭处理"""
        self.control.sendExitRequest()
        self.root.destroy()

    def reportDisplay(self, data):
        """显示回测报告"""
        parent = HistoryToplevel(self, self.root)
        parent.set_config()
        ReportView(data, parent)
        parent.display_()

    def updateStatus(self, strategyIdList, value):
        """
        更新策略状态
        :param strategyIdList: 策略Id列表
        :param value: 更新所选中的策略的状态值（更新所有状态）
        :return:
        """
        self.quant_monitor.updateStatus(strategyIdList, value)

    def delStrategy(self, strategyId):
        """
        删除监控列表中的策略
        :param strategyIdList: 待删除的策略列表
        :return:
        """
        self.quant_monitor.deleteStrategy(strategyId)


