import os

import multiprocessing
import threading
import queue
import traceback
from utils.utils import load_file
from capi.com_types import *
from capi.event import Event


class QuantModel(object):
    def __init__(self, top, ui2eg_queue, eg2ui_queue, logger):
        self._ui2eg_queue = ui2eg_queue
        self._eg2ui_queue = eg2ui_queue
        self._logger = logger
        self._receive = GetEgData(top, self._eg2ui_queue, self._logger)
        self._stManager = self._receive.getStManager()

        # 数据模型
        self.data = []  # 确定需要选用的数据模型
        # 用户选择加载的合约信息
        self._editor = {"path": "", "code": ""}
        self._strategyId = []   # 策略ID
        self._top = top
        self.createReceiveThread()

    def createReceiveThread(self):
        receive_th = threading.Thread(target=self.receiveEgEvent)
        receive_th.daemon = True
        receive_th.start()

    def receiveEgEvent(self):
        """处理engine事件"""
        self._receive.handlerEgEvent()

    def getCurStId(self):
        """获取当前运行的策略ID"""
        return self._receive.getCurStId()

    def getReportData(self):
        return self._receive.getReportData()

    def getEditorText(self):
        return self._editor

    def setEditorTextCode(self, path):
        """设置加载合约的路径信息"""
        self._editor["path"] = path
        if os.path.isfile(path):
            self._editor["code"] = load_file(path)
        else:
            self._editor["code"] = ""

    # TODO:弃用
    def getExecute(self):
        """
        获取运行策略列表
        :return: 运行列表
        """
        executeList = self._stManager.getStrategyDict()
        # tempList = []
        # for id, value in executeList.items():
        #     tempList.append(value)
        # self._executeList = tempList
        return executeList

    def getExchange(self):
        return self._receive.getExchange()

    def getCommodity(self):
        return self._receive.getCommodity()

    def getContract(self):
        return self._receive.getContract()

    def getUserNo(self):
        return self._receive.getUserNo()

    def getStrategyManaegr(self):
        return self._stManager


class SendRequest(object):
    """用于向engine_queue发送请求"""
    def __init__(self, queue):
        self._ui2egQueue = queue

        # 注册发送请求事件
        # self._regRequestCallback()

    # def _regRequestCallback(self):
    #     self._uiRequestCallback = {
    #         EV_UI2EG_LOADSTRATEGY: self.,
    #         EV_UI2EG_REPORT: self.,
    #
    #     }

    def loadRequest(self, path, config):
        """加载请求"""
        msg = {
            'EventSrc'   : EEQU_EVSRC_UI,
            'EventCode'  : EV_UI2EG_LOADSTRATEGY,
            'SessionId'  : None,
            'StrategyId' : 0,
            'UserNo'     : '',
            'Data': {
                'Path' : path,
                'Args' : config,
            }
        }
        event = Event(msg)
        # TODO: 下面队列会阻塞
        try:
            self._ui2egQueue.put(event)
        except:
            print("队列已满, 现在已有消息%s条" % self._ui2egQueue.qsize())
        print("Sending load  Completely")

    def reportRequest(self, strategyId):
        """报告"""
        msg = {
            "EventSrc": EEQU_EVSRC_UI,
            "EventCode": EV_UI2EG_REPORT,
            "SessionId": 0,
            "StrategyId": strategyId,
            "UserNo": "",
            "Data": ""
        }
        event = Event(msg)
        try:
            self._ui2egQueue.put(event)
        except:
            print("队列已满，现在已有消息%s条" % self._ui2egQueue.qsize())

    def quantExitRequest(self):
        """量化界面关闭事件"""
        msg = {
            "EventSrc": EEQU_EVSRC_UI,
            "EventCode": EV_UI2EG_EQUANT_EXIT,
            "SessionId": 0,
            "Data": ""
        }
        event = Event(msg)

        try:
            self._ui2egQueue.put(event)
        except:
            print("队列已满，现在已有消息%s条" % self._ui2egQueue.qsize())

    def strategyPause(self, strategyId):
        """策略暂停事件"""
        msg = {
            "EventSrc": EEQU_EVSRC_UI,
            "EventCode": EV_UI2EG_STRATEGY_PAUSE,
            "SessionId": 0,
            "Data": strategyId
        }

        event = Event(msg)

        self._ui2egQueue.put(event)
        print("暂停事件已发送")

    def strategyResume(self, strategyId):
        """策略运行恢复"""
        msg = {
            "EventSrc": EEQU_EVSRC_UI,
            "EventCode": EV_UI2EG_STRATEGY_RESUME,
            "SessionId": 0,
            "Data": strategyId
        }

        event = Event(msg)
        self._ui2egQueue.put(event)
        print("恢复事件已发送")

    def strategyQuit(self, strategyId):
        """策略停止运行"""
        msg = {
            "EventSrc": EEQU_EVSRC_UI,
            "EventCode": EV_UI2EG_STRATEGY_QUIT,
            "SessionId": 0,
            "Data": strategyId
        }

        event = Event(msg)
        self._ui2egQueue.put(event)
        print("停止事件已发送")


# class AskRequest(object):
#     """用于接收engine_queue的请求，向ui_queue写数据"""
#     def __init__(self, ui2eg_queue, eg2ui_queue):
#         self._ui2eg_queue = ui2eg_queue
#         self._eg2ui_queue = eg2ui_queue
#
#     def send_data(self):
#         try:
#             uiEvent = self._ui2eg_queue.get()
#             eventCode = uiEvent.getEventCode()
#             if eventCode == EV_UI2EG_LOADSTRATEGY:
#                 msg = {
#                     "EventSrc": EEQU_EVSRC_ENGINE,
#                     "EventCode": EV_EG2UI_LOADSTRATEGY_RESPONSE,
#                     "StrategyId": 0,
#                     "Data": {},
#                     "SessionId": 0
#                 }
#             elif eventCode == EV_UI2EG_REPORT:
#                 msg = {
#                     "EventSrc": EEQU_EVSRC_ENGINE,
#                     "EventCode": EV_EG2UI_REPORT_RESPONSE,
#                     "StrategyId": 0,
#                     "Data": {"Fund": 0, "stage": 1, "Orders": 2, "Detail": 3, "KLineType": 4},
#                     "SessionId": 0
#                 }
#             else:
#                 msg = {}
#             eventSend = Event(msg)
#             self._eg2ui_queue.put(eventSend)
#
#         except queue.Empty:
#             print("ui_queue队列为空")


class GetEgData(object):
    """从engine_queue中取数据"""
    def __init__(self, app, queue, logger):
        self._logger = logger
        self._eg2uiQueue = queue
        self._curStId = None  # 当前加载的策略ID
        self._reportData = {}  # 回测报告请求数据
        self._stManager = StrategyManager(app)  # 策略管理器
        self._exchangeList = []
        self._commodityList = []
        self._contractList = []
        self._userNo = []      # 资金账户
        self._app = app

        # 注册引擎事件应答函数
        self._regAskCallback()

    def _regAskCallback(self):
        self._egAskCallbackDict = {
            EV_EG2UI_LOADSTRATEGY_RESPONSE: self._onEgLoadAnswer,
            EV_EG2UI_REPORT_RESPONSE:       self._onEgReportAnswer,
            EV_EG2UI_CHECK_RESULT:          self._onEgDebugInfo,
            EV_EG2ST_MONITOR_INFO:          self._onEgMonitorInfo,
            EV_EG2UI_STRATEGY_STATUS:       self._onEgStrategtStatus,
            EEQU_SRVEVENT_EXCHANGE:         self._onEgExchangeInfo,
            EEQU_SRVEVENT_COMMODITY:        self._onEgCommodityInfo,
            EEQU_SRVEVENT_CONTRACT:         self._onEgContractInfo,
            EEQU_SRVEVENT_TRADE_USERQRY:    self._onEgUserInfo
        }

    # TODO: event.getChian()的类型为字符串：'1', '0'
    def _onEgLoadAnswer(self, event):
        """获取引擎加载应答数据"""
        self._curStId = event.getStrategyId()
        self._stManager.addStrategy(event.getData())

    def _onEgReportAnswer(self, event):
        """获取引擎报告应答数据并显示报告"""
        data = event.getData()
        self._reportData = data
        # 取到报告数据弹出报告
        if self._reportData:
            self._app.reportDisplay(self._reportData)

    def _onEgDebugInfo(self, event):
        """获取引擎策略调试信息"""
        data = event.getData()
        if data:
            errText = data["ErrorText"]
            self._logger.err_error(errText)

    def _onEgMonitorInfo(self, event):
        """获取引擎实时推送监控信息"""
        # TODO: data中包含的数据太多
        # stId = event.getStrategyId()
        # data = event.getData()
        # 实时更新监控界面信息
        # self._stManager.addStrategyData(stId, data)
        # self._stManager.updateStrategyStatus(stId, data["StrategyState"])
        pass

    def _onEgExchangeInfo(self, event):
        """获取引擎推送交易所信息"""
        exData = event.getData()
        self._exchangeList.extend(exData)

    def _onEgCommodityInfo(self, event):
        """获取引擎推送品种信息"""
        commData = event.getData()
        self._commodityList.extend(commData)

    def _onEgContractInfo(self, event):
        """获取引擎推送合约信息"""
        contData = event.getData()
        self._contractList.extend(contData)

    def _onEgUserInfo(self, event):
        """获取引擎推送资金账户"""
        # if event.getChain() == '0':  # 信息发送完成标志
        #     self.isChian = False
        userInfo = event.getData()
        self._userNo.extend(userInfo)

        self._app.setLoadState()

    def _onEgStrategtStatus(self, event):
        """接收引擎推送策略状态改变信息"""
        id = event.getStrategyId()
        sStatus = event.getData()["Status"]

        if id not in self._stManager.getStrategyDict():
            dataDict = {
                "StrategyId":   id,
                "Status":       sStatus
            }
            self._stManager.add_(dataDict)
            self._stManager.updateStrategyStatus(id, sStatus)
        else:
            # TODO：策略状态改变后要通知监控界面
            self._stManager.updateStrategyStatus(id, sStatus)

            data = self._stManager.getSingleStrategy(id)

            self._app.updateStatus([id], (id, ['StrategyName'], "1", "2"))

    def handlerEgEvent(self):
        while True:
            event = self._eg2uiQueue.get()
            eventCode = event.getEventCode()
            if eventCode not in self._egAskCallbackDict:
                self._logger.error("Unknown engine event(%d)"%eventCode)
                continue
            self._egAskCallbackDict[eventCode](event)

    def getReportData(self):
        if self._reportData:
            return self._reportData
        return None

    def getCurStId(self):
        if self._curStId:
            return self._curStId
        return None

    def getStManager(self):
        return self._stManager

    def getExchange(self):
        """取得接收到的交易所信息"""
        return self._exchangeList

    def getCommodity(self):
        """品种"""
        return self._commodityList

    def getContract(self):
        """合约"""
        return self._contractList

    def getUserNo(self):
        """资金账户"""
        return self._userNo


class StrategyManager(object):
    def __init__(self, app):
        self._app = app
        self._strategyDict = {}

    def addStrategy(self, dataDict):
        id = dataDict['StrategyId']
        self._strategyDict[id] = dataDict
        self._app.updateSingleExecute(dataDict)

    def add_(self, dataDict):
        #TODO: 策略状态传过来事件问题
        id = dataDict['StrategyId']
        self._strategyDict[id] = dataDict

    def addStrategyData(self, id, data):
        self._strategyDict[id].update({"Data": data})

    def removeStrategy(self, id):
        #TODO: 什么时候remove？
        if id in self._strategyDict:
            self._strategyDict.pop(id)

    def queryStrategyStatus(self, id):
        return self._strategyDict[id]["Status"]

    def queryStrategyRunType(self, id):
        return self._strategyDict[id]["RunType"]

    def getStrategyData(self, id):
        return self._strategyDict[id]["Data"]

    def queryStrategyName(self, id):
        return self._strategyDict[id]["StrategyName"]

    def updateStrategyStatus(self, id, status):
        self._strategyDict[id]["Status"] = status

    def getStrategyDict(self):
        return self._strategyDict

    def getSingleStrategy(self, id):
        return self._strategyDict[id]