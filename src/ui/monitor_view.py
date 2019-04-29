import os
from tkinter import *
from tkinter import ttk, messagebox, Frame
from utils.utils import *
from .language import Language
from .com_view import QuantFrame, QuantToplevel
from .editor import MonitorText, SignalText, ErrorText
from .menu import RunMenu
from capi.com_types import *


class QuantMonitor(object):

    # 背景色
    bgColor = rgb_to_hex(245, 245, 245)
    bgColorW = "white"

    def __init__(self, frame, control, language):
        self.parentFrame = frame
        self._controller = control
        self.language = language

        # 初始化策略状态字典
        self._initStrategyStatus()
        # 策略编号初始值
        self._strategyNum = 1

        # Monitor不同标签的背景色
        self.rColor = self.bgColorW
        self.lColor = self.bgColor
        self.sColor = self.bgColor
        self.eColor = self.bgColor

        self.createButtonFrame()

        # 执行列表、监控日志、信号记录、错误
        self.executeList = Frame(self.parentFrame)
        self.monitorLog = Frame(self.parentFrame)
        self.sigRecord = Frame(self.parentFrame)
        self.errRecord = Frame(self.parentFrame)

        self.executeList.pack(side=TOP, fill=BOTH, expand=YES)

        self.monText = None
        self.sigText = None
        self.errText = None

    def createButtonFrame(self):
        btnFrame = Frame(self.parentFrame, height=30, bg=self.bgColor)
        btnFrame.pack_propagate(0)
        btnFrame.pack(side=TOP, fill=X)
        # 利用frame做出button的黑色边框
        # f1 = Frame(btnFrame, highlightbackground="black", highlightthickness=1, bd=0)
        # f1.pack(side=LEFT)

        self.runBtn = Button(btnFrame, text="策略运行", relief=FLAT, padx=14, pady=1.5, bg=self.rColor,
                             bd=0, highlightthickness=1, command=self.toMonFrame)
        self.logBtn = Button(btnFrame, text="运行日志", relief=FLAT, padx=14, pady=1.5, bg=self.lColor,
                             bd=0, highlightthickness=1,
                             command=self.toLogFrame)
        self.sigBtn = Button(btnFrame, text="信号记录", relief=FLAT, padx=14, pady=1.5, bg=self.sColor,
                             bd=0, highlightthickness=1,  command=self.toSigFrame)
        self.errBtn = Button(btnFrame, text="错误信息", relief=FLAT, padx=14, pady=1.5, bg=self.eColor,
                             bd=0, highlightthickness=1, command=self.toErrFrame)
        self.runBtn.pack(side=LEFT, expand=NO)
        self.logBtn.pack(side=LEFT, expand=NO)
        self.sigBtn.pack(side=LEFT, expand=NO)
        self.errBtn.pack(side=LEFT, expand=NO)

        for btn in (self.runBtn, self.logBtn, self.sigBtn, self.errBtn):
            btn.bind("<Enter>", self.handlerAdaptor(self.onEnter, button=btn))
            btn.bind("<Leave>", self.handlerAdaptor(self.onLeave, button=btn))

    def createMonitor(self):
        # monitorRightBar = Scrollbar(self.monitorLog)
        # monitorRightBar.pack(side=RIGHT, fill=Y), yscrollcommand=monitorRightBar.set

        self.monText = MonitorText(self.monitorLog, height=20, bd=0)
        self.monText.createScrollbar()
        self.monText.pack(fill=BOTH, expand=YES)

    def createSignal(self):
        self.sigText = SignalText(self.sigRecord, height=20, bd=0)
        self.sigText.createScrollbar()
        self.sigText.pack(fill=BOTH, expand=YES)

    def createExecute(self):
        # headList = ["编号", "策略名称", "策略状态", "最终权益", "胜率", "净利润", "总盈利", "总亏损", "可用资金",
        #              "夏普比率", "风险率", "手续费", "最大资产回撤", "最大资产回撤时间", "资产最大值", "资产最小值",
        #              "最大连续盈利次数", "最大连续亏损次数"]
        # headList = ["编号", "策略名称", "策略状态", "频率","保证金比例", "手续费",
        #             "初始资金", "总盈利", "总亏损", "可用资金"]
        # headList = ["编号", "策略名称", "策略状态", "运行类型", "初始资金", "合约", "开始时间", "结束时间", "权益"]
        headList = ["编号", "策略名称", "合约", "策略状态", "运行类型"]

        self.executeBar = ttk.Scrollbar(self.executeList, orient="vertical")
        self.executeBar.pack(side=RIGHT, fill=Y)

        self.executeListTree = ttk.Treeview(self.executeList, show="headings", height=28, columns=tuple(headList),
                                            yscrollcommand=self.executeBar.set, style="Filter.Treeview")
        self.executeBar.config(command=self.executeListTree.yview)
        self.executeListTree.pack(fill=BOTH, expand=YES)

        self.executeListTree.bind("<Button-3>", self.createMenu)

        for key in tuple(headList):
            self.executeListTree.column(key, minwidth=20, width=55, anchor=CENTER)
            self.executeListTree.heading(key, text=key)

    def createMenu(self, event):
        """创建运行策略右键菜单"""
        RunMenu(self._controller, self.executeListTree).popupmenu(event)

    # ----------------弃用--------------------
    def updateExecuteList(self, executeList):
        for child in self.executeListTree.get_children():
            self.executeListTree.delete(child)

        number = 0
        for stId, execute in executeList.items():

            #TODO:先不放executeList的"data"
            values = [
                number,
                execute["StrategyName"],
                execute["Status"],
                execute["RunType"]
            ]
            # TODO：应该把策略id信息放到values中，方便后续处理
            self.executeListTree.insert("", END, iid=stId, values=tuple(values), tag=0)
            number += 1

    def _initStrategyStatus(self):
        self.statusDict = {
            ST_STATUS_NONE:         "初始状态",
            ST_STATUS_HISTORY:      "历史回测",
            ST_STATUS_CONTINUES:    "实时触发",
            ST_STATUS_PAUSE:        "暂停",
            ST_STATUS_QUIT:         "停止"
        }

    def _getStrategyStatus(self, key):
        return self.statusDict[key]

    def updateSingleExecute(self, dataDict):
        status = self._getStrategyStatus(dataDict["StrategyState"])
        runType = '历史回测' if dataDict['Config']['RunMode']['Actual']['SendOrder2Actual'] else "实盘运行"

        print("dataDict: ", dataDict)

        values = [
            dataDict['StrategyId'],
            dataDict['StrategyName'],
            dataDict['Config']['Contract'],
            status,
            runType,
        ]
        self.executeListTree.insert("", END, iid=dataDict['StrategyId'], values=tuple(values), tag=0)

    def createErr(self):
        # 错误信息展示
        self.errText = ErrorText(self.errRecord, height=20, bd=0)
        self.errText.createScrollbar()
        self.errText.pack(fill=BOTH, expand=YES)

    def updateRun(self):
        pass

    def updateLogText(self):
        guiQueue = self._controller.get_logger().getGuiQ()

        try:
            data = guiQueue.get_nowait()
        except:
            return
        else:
            self.monText.setText(data)

    def updateSigText(self):
        sigQueue = self._controller.get_logger().getSigQ()
        try:
            sigData = sigQueue.get_nowait()
        except:
            return
        else:
            # self.toSigFrame()
            self.sigText.setText(sigData)

    def updateErrText(self):
        errQueue = self._controller.get_logger().getErrQ()
        try:
            errData = errQueue.get_nowait()
        except:
            return
        else:
            self.toErrFrame()
            self.errText.setText(errData)

    def toMonFrame(self):
        self.runBtn.config(bg="white")
        self.rColor = self.runBtn['bg']
        self.lColor = self.bgColor
        self.sColor = self.bgColor
        self.eColor = self.bgColor
        self.errBtn.config(bg=self.rColor)
        self.sigBtn.config(bg=self.sColor)
        self.logBtn.config(bg=self.lColor)
        self.monitorLog.pack_forget()
        self.sigRecord.pack_forget()
        self.errRecord.pack_forget()
        self.executeList.pack(side=TOP, fill=BOTH, expand=YES)

    def toLogFrame(self):
        self.logBtn.config(bg="white")
        self.lColor = self.logBtn['bg']
        self.rColor = self.bgColor
        self.sColor = self.bgColor
        self.eColor = self.bgColor
        self.runBtn.config(bg=self.rColor)
        self.sigBtn.config(bg=self.sColor)
        self.errBtn.config(bg=self.eColor)
        self.sigRecord.pack_forget()
        self.executeList.pack_forget()
        self.errRecord.pack_forget()
        self.monitorLog.pack(side=TOP, fill=BOTH, expand=YES)

    def toSigFrame(self):
        self.sigBtn.config(bg="white")
        self.sColor = self.sigBtn['bg']
        self.lColor = self.bgColor
        self.rColor = self.bgColor
        self.eColor = self.bgColor
        self.runBtn.config(bg=self.rColor)
        self.logBtn.config(bg=self.lColor)
        self.errBtn.config(bg=self.eColor)
        self.monitorLog.pack_forget()
        self.executeList.pack_forget()
        self.errRecord.pack_forget()
        self.sigRecord.pack(side=TOP, fill=BOTH, expand=YES)

    def toErrFrame(self):
        self.errBtn.config(bg="white")
        self.eColor = self.errBtn['bg']
        self.lColor = self.bgColor
        self.rColor = self.bgColor
        self.sColor = self.bgColor
        self.runBtn.config(bg=self.rColor)
        self.sigBtn.config(bg=self.sColor)
        self.logBtn.config(bg=self.lColor)
        self.parentFrame.update()
        self.monitorLog.pack_forget()
        self.executeList.pack_forget()
        self.sigRecord.pack_forget()
        self.errRecord.pack(side=TOP, fill=BOTH, expand=YES)

    def handlerAdaptor(self, fun, **kwargs):
        return lambda event, fun=fun, kwargs=kwargs: fun(event, **kwargs)

    def onEnter(self, event, button):
        if button == self.runBtn:
            button.config(bg='white')
            self.logBtn.config(bg=self.bgColor)
            self.sigBtn.config(bg=self.bgColor)
            self.errBtn.config(bg=self.bgColor)
        elif button == self.logBtn:
            button.config(bg='white')
            self.runBtn.config(bg=self.bgColor)
            self.sigBtn.config(bg=self.bgColor)
            self.errBtn.config(bg=self.bgColor)
        elif button == self.sigBtn:
            button.config(bg='white')
            self.runBtn.config(bg=self.bgColor)
            self.logBtn.config(bg=self.bgColor)
            self.errBtn.config(bg=self.bgColor)
        else:
            button.config(bg='white')
            self.runBtn.config(bg=self.bgColor)
            self.logBtn.config(bg=self.bgColor)
            self.sigBtn.config(bg=self.bgColor)

    def onLeave(self, event, button):
        button.config(bg=rgb_to_hex(227, 230, 233))
        if button == self.runBtn:
            button['bg'] = self.rColor
            self.logBtn['bg'] = self.lColor
            self.sigBtn['bg'] = self.sColor
            self.errBtn['bg'] = self.eColor
        elif button == self.logBtn:
            button['bg'] = self.lColor
            self.runBtn['bg'] = self.rColor
            self.sigBtn['bg'] = self.sColor
            self.errBtn['bg'] = self.eColor
        elif button == self.sigBtn:
            button['bg'] = self.sColor
            self.runBtn['bg'] = self.rColor
            self.logBtn['bg'] = self.lColor
            self.errBtn['bg'] = self.eColor
        else:
            button['bg'] = self.eColor
            self.runBtn['bg'] = self.rColor
            self.logBtn['bg'] = self.lColor
            self.sigBtn['bg'] = self.sColor

    def deleteStrategy(self, strategyId):
        """删除策略"""
        self.executeListTree.delete(strategyId)

    def updateStatus(self, strategyIdList, value):
        """更新策略ID对应的策略状态"""
        for id in strategyIdList:
            self.executeListTree.set(id, value=value)

