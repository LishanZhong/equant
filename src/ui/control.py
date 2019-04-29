import threading
import time

from tkinter import Tk
from tkinter import messagebox
from .model import QuantModel, SendRequest
from .view import QuantApplication
from .language import *
from report.reportview import ReportView
from .com_view import HistoryToplevel

from utils.utils import save


class TkinterController(object):
    '''程序化入口类'''

    def __init__(self, logger, ui2eg_q, eg2ui_q):

        #日志对象
        self.logger = logger
        #初始化多语言
        load_language("config")
        self._ui2egQueue = ui2eg_q
        self._eg2uiQueue = eg2ui_q

        # UI2EG发送请求对象
        self._request = SendRequest(self._ui2egQueue)

        # 创建主窗口
        self.top = Tk()
        self.app = QuantApplication(self.top, self)
        self.app.create_window()
        # 设置日志更新
        self.update_log()

        # 创建模块
        self.model = QuantModel(self.app, self._ui2egQueue, self._eg2uiQueue, self.logger)
        self.logger.info("Create quant model!")

        #TODO: 暂时先这样调用
        # self.app.setLoadState()

    def get_logger(self):
        return self.logger

    def update_log(self):
        self.app.updateLogText()
        self.app.updateSigText()
        self.app.updateErrText()
        #TODO:
        self.top.after(10, self.update_log)

    def run(self):
        #启动主界面线程
        self.app.mainloop()
        
    def set_help_text(self, funcName, text):
        self.app.set_help_text(funcName, text)

    def setEditorTextCode(self, path):
        """设置当前编辑的策略路径和代码信息"""
        self.model.setEditorTextCode(path)

    def getEditorText(self):
        return self.model.getEditorText()

    def getStManager(self):
        """获取策略管理器"""
        return self.model.getStrategyManaegr()

    def saveStrategy(self):
        """保存当前策略"""
        self.app.quant_editor.saveEditor()

    def load(self, strategyPath):
        """加载合约事件"""
        self.app.createLoadWin()

        config = self.app.loadWin.getConfig()
        if config:   # 获取到config
            self._request.loadRequest(strategyPath, config)
            self.logger.info("load strategy")
            return

        return

    def generateReportReq(self):
        """发送生成报告请求"""
        # TODO：生成报告，如果RepData为空，则显示最新日期的历史报告，
        # TODO：不为空，代表获取到的数据为传过来的数据
        strategyId = self.model.getCurStId()
        if strategyId:
            self._request.reportRequest(strategyId)

    def newStrategy(self, path):
        """右键新建策略"""
        if not os.path.exists(path):
            f = open(path, "w")
            f.write('\n'
                    'def initialize(context): \n    pass\n\n\n'
                    'def handle_data(context):\n    pass')
            f.close()

        # 更新策略路径
        self.setEditorTextCode(path)

        self.app.updateStrategyTree(path)

        # 更新策略编辑界面内容
        self.updateEditor(path)

    def newDir(self, path):
        """策略目录右键新建文件夹"""
        if not os.path.exists(path):
            os.makedirs(path)
        self.app.updateStrategyTree(path)

    def updateEditor(self, path):
        """
        更新策略编辑的内容和表头
        :param path: 策略路径，为空则将编辑界面内容置为空
        :return:
        """
        editor = self.getEditorText()
        file = os.path.basename(path)

        self.app.updateEditorHead(file)
        self.app.updateEditorText(editor["code"])

    def sendExitRequest(self):
        """发送量化界面退出请求"""
        self._request.quantExitRequest()

    def pauseRequest(self, strategyIdList):
        """
        发送所选策略暂停请求
        :param strategyId: 所选策略Id列表
        :return:
        """
        for id in strategyIdList:
            self._request.strategyPause(id)

    def resumeRequest(self, strategyIdList):
        """
        发送所选策略恢复运行请求
        :param strategyId: 所选策略Id列表
        :return:
        """
        for id in strategyIdList:
            self._request.strategyResume(id)

    def quitRequest(self, strategyIdList):
        """
        发送所选策略停止请求
        :param strategyId:  所选策略Id列表
        :return:
        """
        for id in strategyIdList:
            self._request.strategyQuit(id)

    def delStrategy(self, strategyIdList):
        # 获取策略管理器
        strategyManager = self.getStManager()
        for id in strategyIdList:
            self.app.delStrategy(id)
            #将策略管理器中的该策略也删除掉
            strategyManager.removeStrategy(id)


# 线程
# ---------------------弃用-------------------------
class UIThread(threading.Thread):

    def __init__(self, target):
        super(UIThread, self).__init__()
        self.__flag = threading.Event()
        self.__flag.set()
        self.__running = threading.Event()
        self.__running.set()
        self.__target = target
        self.daemon = True
        self._state = False

    def getstate(self):
        return self._state

    def run(self):
        while self.__running.isSet():
            self.__flag.wait()
            self.__target()
            time.sleep(1)

    def pause(self):
        self._state = True
        self.__flag.clear()

    def resume(self):
        self._state = False
        self.__flag.set()
        self.__running.clear()

    def stop(self):
        self.__flag.set()
        self.__running.clear()
