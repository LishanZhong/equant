import importlib
from SharedImport import *
import base_api


def isMsgEnd(msg):
    return msg.isMsgEnd()


class MsgWrapper:
    def __init__(self, msg):
        self._msg = msg

    def getData(self):
        return self._msg["SrvData"]

    def getContractNo(self):
        return self._msg["ContractNo"].decode()

    def getService(self):
        return self._msg["SrvSrc"]

    def getEvent(self):
        return self._msg["SrvEvent"]

    def getAssetsData(self):
        assert self._msg["SrvSrv"] == QuantDataType.Service.OnTimeAssets.value and \
               self._msg["SrvEvent"] == QuantDataType.OnTimeAssetsEvent.snap.value, "error"
        return self._msg["SrvData"]["FieldData"]

    def isMsgEnd(self):
        return self._msg["SrvChain"] == QuantDataType.ChainEnd.End.value

    def getKLineType(self):
        return self._msg["KLineType"]


# 即时行情，分为 tick、秒线、分钟线、日线、自定义
class OnTimeAssets:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls, *args, **kwargs)
            print("create singleton instance of Assets ", cls._instance)
        else:
            print("Assets instance has existed")
        return cls._instance
    
    def __init__(self):
        # 全量交易所、品种、合约
        self._exchangeData = []
        self._commodityData = []
        self._contractData = []
        self._isBaseDataEnd = {"ExchangeData": True, "CommodityData": True, "ContractData": True}
        self._counts = {"ExchangeData": 0, "CommodityData": 0, "ContractData": 0}

        # tick
        self._tickData = {}

        #
        self._test = False

    # 每次请求可能有多个msg，本方法被触发多次
    def updateData(self, msg):
        event = msg.getEvent()
        if event == QuantDataType.OnTimeAssetsEvent.Exchange.value:
            self._updateExchange(msg)
        elif event == QuantDataType.OnTimeAssetsEvent.Commodity.value:
            self._updateCommodity(msg)
        elif event == QuantDataType.OnTimeAssetsEvent.Contract.value:
            self._updateContract(msg)
        # tick事件
        elif event == QuantDataType.OnTimeAssetsEvent.Snap.value:
            assert msg.isMsgEnd() and len(msg.getData()) <= 1, "error "
            self._updateTick(msg)
        elif event == QuantDataType.OnTimeAssetsEvent.Connect.value:
            raise NotImplementedError
        else:
            errMsg = f"event {event} is not handled in Assets Service"
            raise ValueError(errMsg)

    def _updateTick(self, msg):
        if msg.getContractNo() not in self._tickData:
            self._tickData[msg.getContractNo()] = [np.nan]*len(QuantDataType.WholeAssetsFields)
        for tick in msg.getData():
            for record in tick["FieldData"]:
                self._tickData[msg.getContractNo()][record["FieldMean"]] = record["FieldValue"]

        print(self._tickData)

    def getData(self, kLineType, contractNo):
        if kLineType == QuantDataType.KLineType.Tick.value:
            return self._tickData[contractNo]
        else:
            # raise NotImplementedError
            return {}
    # # 获取tick
    # def getCurrentTick(self, contracts={}):
    #     return self._tickData
    #     # return {contract:self._tickData[contract] for contract in contracts}

    # 取消即时行情订阅后，清理数据模型
    def unRegContract(self, contracts):
        pass

    # 交易所
    def _updateExchange(self, msg):
        records = msg["SrvData"]
        if self._isBaseDataEnd["ExchangeData"] is True:
            # 全量数据分多个包
            self._exchangeData = []
            self._isBaseDataEnd["ExchangeData"] = False
        self._exchangeData.extend(records)
        self._isBaseDataEnd["ExchangeData"] = msg.isMsgEnd()

        if self._isBaseDataEnd["ExchangeData"] is True:
            print(self._exchangeData)
            self._counts["ExchangeData"] = len(self._exchangeData)

    # 品种
    def _updateCommodity(self, msg):
        records = msg["SrvData"]
        if self._isBaseDataEnd["CommodityData"] is True:
            # 全量数据分多个包
            self._commodityData = []
            self._isBaseDataEnd["CommodityData"] = False
        self._commodityData.extend(records)
        self._isBaseDataEnd["CommodityData"] = msg.isMsgEnd()

        if self._isBaseDataEnd["CommodityData"] is True:
            print(self._commodityData)
            self._counts["CommodityData"] = len(self._commodityData)

    # 合约
    def _updateContract(self, msg):
        records = msg["SrvData"]
        if self._isBaseDataEnd["ContractData"] is True:
            # 全量数据分多个包
            self._contractData = []
            self._isBaseDataEnd["ContractData"] = False
        self._contractData.extend(records)
        self._isBaseDataEnd["ContractData"] = isMsgEnd(msg)

        # def getExchangeData(self):
        #     if not self._isBaseDataEnd["ExchangeData"]:
        #         print("交易请求的结果尚未处理完")
        #         return []
        #     return self._exchangeData
        #
        # def getCommodityData(self):
        #     if not self._isBaseDataEnd["CommodityData"]:
        #         print("品种请求的结果尚未处理完")
        #         return []
        #     return self._commodityData
        #
        # def getContractData(self):
        #     if not self._isBaseDataEnd["ContractData"]:
        #         print("合约请求的结果尚未处理完")
        #         return []
        #     return self._contractData

        if self._isBaseDataEnd["ContractData"] is True:
            self._counts["ContractData"] = len(self._contractData)
            # self._contractAssetsData = pd.DataFrame(self._contractData, columns=self._fields)
            # self._contract2Index = pd.Series(
            #     self._contractAssetsData.ContractNo.values,
            #     index = self._contractAssetsData.index.values
            # ).to_dict()
            # print(self._contractAssetsData)
            self._test = True

        if self._test is True:
            print("交易所数量：", self._counts["ExchangeData"],
                  " 品种数量: ", self._counts["CommodityData"],
                  " 合约总量: ", self._counts["ContractData"])
            print(isMsgEnd(msg))


# 历史行情
class HisAssets:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls, *args, **kwargs)
            # print("create singleton instance of HisAssets ", cls._instance)
        else:
            print("HisAssets instance has existed")
        return cls._instance
    
    def __init__(self):
        self._tickFields = [
            "ContractNo", "CommodityNo", "ExchangeNo", "DataTimestamp", "IsChanged", "IsSent", "Pid"
        ]
        self._tickData = {
            "CFFEX|F|IF|1905":[{},{}]
        }
        self._index = {
            ("ContractNo", "begin date", "end date"):0
        }

    #
    def updateData(self, msg):
        for record in msg["SrvData"]:
            if record["ContractNo"] not in self._tickData:
                self._tickData[record["ContractNo"]] = []
            self._tickData[record["ContractNo"]].append(record)

    def getClose(self):
        return list(self._tickData.values())


# 交易数据
class Trade:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls, *args, **kwargs)
            # print("create singleton instance of Trade ", cls._instance)
        else:
            print("Trade instance has existed")
        return cls._instance
    
    def __init__(self):
        pass


class DataModel:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls, *args, **kwargs)
            # print("create singleton instance of DataModel ", cls._instance)
        else:
            print("DataModel instance has existed")
        return cls._instance
    
    def __init__(self):
        self._onTimeAssets = OnTimeAssets()
        self._hisAssets = HisAssets()
        self._trade = Trade()
        # self._hisOnTimeData = HisOnTimeAssets()

    def getTrade(self):
        return self._trade

    def getHisAssets(self):
        return self._hisAssets

    def getOnTimeAssets(self):
        return self._onTimeAssets

    # 假设仅有历史行情中会有收盘价
    def getClose(self):
        return self.getHisAssets().getClose()


class StragetyIdGenerator:
    # 单例模式。单进程有效。
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls, *args, **kwargs)
            # print("create singleton instance of PyAPI ", cls._instance)
        else:
            print("PyAPI instance has existed")
        return cls._instance

    def __init__(self):
        self._id = 1

    def getId(self):
        id = self._id
        self._id += 1
        return f"strategy-{id}"


# 策略
class Stragety:
    def __init__(self, args):
        self._strategyId = args["StragetyId"]
        self._filePath = args["FilePath"]

    def _initSubscribeInfo(self):
        self._subscribeInfo = None
        if self._userModule is not None:
            self._userModule.initialize(self._context)
            self._contracts = self._context.contracts
            self._subscribeInfo = SubscribeInfo()

    def start(self, commQueues, enginePid):
        self._moduleName, curPath = os.path.splitext(os.path.split(self._filePath)[-1])
        if curPath not in sys.path:
            sys.path.insert(0, curPath)
        self._userModule = self._importModule(self._moduleName)
        self._scope = {} if self._userModule is None else self._userModule.__dict__
        self._context = StrategyContext()
        self._contracts = None
        self._initSubscribeInfo()
        self._dataModel = DataModel()
        ApplicationAPI = base_api.BaseApi(self, self._dataModel)
        self._queues = commQueues
        self._strategyPid = os.getpid()
        self._enginePid = enginePid
        self._scope.update(sys.modules["base_api"].__dict__)
        self._scope["ApplicationAPI"].updateData(self, self._dataModel)
        self._userModule = self._importModule(self._moduleName, self._scope)

        # print(" this is t", multiprocessing.current_process().name, self._strategyId)
        try:
            while True:
                self._updateData()
                # self._userModule.handle_data(self._context)
                time.sleep(0.01)
        except Exception as e:
            print("strategy ", self._strategyId, " run fails")
            traceback.print_exc()
            event = Event({"EventCode":QuantDataType.ProcessEvent.SrcProcessEnd.value})
            self.sendEvent(event, self._queues["Strategy2EngineQueue"])

    def getStrategyId(self):
        return self._strategyId

    def getPid(self):
        return self._strategyPid

    def getSubscribeInfo(self):
        return SubscribeInfo()

    #
    def _importModule(self, moduleName, scope = None):
        module = None
        try:
            module = importlib.__import__(moduleName, globals=scope)
        except Exception as e:
            traceback.print_exc()
        finally:
            return module

    # clear queue
    def clear(self, someQueue):
        try:
            while True:
                someQueue.get_nowait()
        except queue.Empty:
            pass

    # 发送事件
    def sendEvent(self, event, someQueue):
        while True:
            try:
                someQueue.put_nowait(event)
                break
            except queue.Full as e:
                print("from sub substrategy queue full, error")

        if event.isExitEvent():
            os._exit(0)

    # 处理主进程发送的事件
    def handleEvent(self, event):
        if event.isExitEvent():
            os._exit(0)
        else:
            kLineType = event.getKLineType()
            contractNo = event.getContractNo()
            data = event.getData()
            print(kLineType, contractNo, data)
            # raise NotImplementedError
            if event.getEventCode() == QuantDataType.ProcessEvent.OnTimeSnap.value:
                if event.getDataType() == "OnTimeAssets" and event.getKLineType() == "Tick" and \
                event.getContractNo() == "CFFEX|F|IF|1905":
                    msg = {
                        "SrvSrc":ord('Q'),
                        "SrvEvent":0x22,
                        "SrvChain":48,
                        "SrvData":[],
                        "ContractNo":b"CFFEX|F|IF|1905"
                    }
                    msg = MsgWrapper(msg)
                    self._dataModel.getOnTimeAssets().updateData(msg)
                    self._userModule.handle_data(self._context)
                    print("in strategy process")
                    print(self._dataModel.getOnTimeAssets()._tickData)

    #
    def _updateData(self):
        try:
            event = self._queues["Engine2StrategyQueue"].get_nowait()
            self.handleEvent(event)
        except queue.Empty as e:
            pass


# 策略及进程管理器
class StrategyProcessMgr:
    def __init__(self):
        self._pid2All = {}
        self._strategyId2Pid = {}

        # 等待退出的子进程,要么engine进程发送退出事件阻塞，要么等待子进程处理结束事件。
        self._eventsWaited = {}

        # 每轮主进程最多处理一个策略进程的请求数。
        self._maxReqHandledPerCycle = 10

    # 一个策略， 对应一个进程、若干队列。
    def insert(self, process, strategy, queues):
        self._pid2All[process.pid] = (process, strategy, queues)
        self._strategyId2Pid[strategy.getStrategyId()] = process.pid
            
    #
    def exitProcessByPid(self, pid):
        event = Event({
            "EventCode": QuantDataType.ProcessEvent.RequestEnd.value,
            "SrcProcessId": os.getpid(),
            "DesProcessId": pid,
            "Parameter": {},
            "Data": []
        })
        self.sendEvent(pid, event)

    def exitProcessByStrategyId(self, strategyId):
        self.exitProcessByPid(self._strategyId2Pid[strategyId])

    def exitAllProcess(self):
        for pid, v in self._pid2All.items():
            v[0].terminate()
            v[0].join
            # self.exitProcessByPid(pid)

    # 父进程向子进程发送退出信号后 或 收到子进程退出信号后，清理。
    def clear(self, pid):
        del self._strategyId2Pid[self._pid2All[0].getStrategyId()]
        del self._pid2All[pid]
        if pid in self._eventsWaited:
            self._eventsWaited[pid] = None

    #
    def sendEvent(self, pid, event):
        engine2StrategyQueue = self._pid2All[pid][2]["Engine2StrategyQueue"]
        try:
            engine2StrategyQueue.put_nowait(event)
        except queue.Full as e:
            if event.isExitEvent():
                self._eventsWaited[pid] = event
            else:
                print("warning, queue full, data abandoned")
                raise queue.Full

    # engine进程向子进程发送事件
    def putData(self, events):
        for event in events:
            pid = event.getRecord()["DesProcessId"]
            assert pid in self._pid2All, "error"
            if pid in self._eventsWaited:
                self.sendEvent(pid, self._eventsWaited[pid])
            else:
                self.sendEvent(pid, event)

    # 子进程向engine发送信息
    def getData(self):
        result = []
        for pid, item in self._pid2All.items():
            count = 0
            strategy2EngineQueue = item[2]["Strategy2EngineQueue"]
            while True:
                try:
                    event = strategy2EngineQueue.get_nowait()
                    result.append(event)
                    count += 1
                    if count >= self._maxReqHandledPerCycle:
                        break
                except queue.Empty as e:
                    break
        # print("本轮请求为：", result)
        return result


# 进程之间通讯接口
class Event:
    def __init__(self, arg):
        self._record = arg

    def getContractNo(self):
        return self._record["ContractNo"]

    def getKLineType(self):
        # return self._record["KLineType"]
        return "Tick"

    def getEventCode(self):
        return self._record["EventCode"]

    def getDataType(self):
        return self._record["DataType"]

    def getData(self):
        return self._record["Data"]

    def updateData(self, data):
        pass

    def getRecord(self):
        return self._record

    def isExitEvent(self):
        return self._record["EventCode"] == QuantDataType.ProcessEvent.DesProcessEnd.value or \
               self._record["EventCode"] == QuantDataType.ProcessEvent.SrcProcessEnd.value

    def isTickEvent(self):
        return self._record["EventCode"] == QuantDataType.ProcessEvent.Tick.value

    def isSecondEvent(self):
        return self._record["EventCode"] == QuantDataType.ProcessEvent.Second.value

    def isMinuteEvent(self):
        return self._record["EventCode"] == QuantDataType.ProcessEvent.Minute.value

    def isDayEvent(self):
        return self._record["EventCode"] == QuantDataType.ProcessEvent.Day.value

    def isUserDefineEvent(self):
        return self._record["EventCode"] == QuantDataType.ProcessEvent.UserDefine.value

    def isDataEvent(self):
        return self._record["EventCode"] == QuantDataType.ProcessEvent.Data.value


# 事件正在被哪些进程监听
# 进程正在监听哪些事件
# class EventMgr:
#     def __init__(self):
#         self._eventCodes = set()    # 事件集合
#         self._pids = set()          # 进程集合
#         self._eventCode2Pids = {}   # 监听某事件的所有进程
#         self._pid2EventCodes = {}   # 某进程监听的所有事件
#
#     # 某个进程监听了某个事件
#     def insert(self, eventCode, pid):
#         if eventCode not in self._eventCodes:
#             self._eventCodes.add(eventCode)
#             self._eventCode2Pids[eventCode] = []
#         if pid not in self._pids():
#             self._pids.add(pid)
#             self._pid2EventCodes[pid] = []
#
#         if pid not in self._eventCode2Pids[eventCode]:
#             self._eventCode2Pids[eventCode].append(pid)
#         if eventCode not in self._pid2EventCodes[pid]:
#             self._pid2EventCodes[pid].append(eventCode)
#
#     def removeEvent(self, eventCode):
#         if eventCode not in self._eventCodes:
#             return
#         self._eventCodes.remove(eventCode)
#         del self._eventCode2Pids[eventCode]
#
#     # 进程退出时，
#     def removeProcess(self, somePid):
#         for eventCode, pids in self._eventCode2Pids:
#             self._eventCode2Pids[eventCode] = [pid for pid in pids if pid != somePid]
#
#         if somePid in self._pids:
#             self._pids.remove(somePid)
#             del self._pid2EventCodes[somePid]
#
#     def removeProcessEvent(self, somePid, eventCode):
#         event2Pids = self._eventCode2Pids[eventCode]
#         self._eventCode2Pids[eventCode] = [pid for pid in event2Pids if pid != somePid]
#
#         if somePid in self._pids and eventCode in self._pid2EventCodes[somePid]:
#             self._pid2EventCodes[somePid].remove(eventCode)
#
#     def getEventPids(self, eventCode):
#         if eventCode not in self._eventCodes:
#             return []
#         return self._eventCode2Pids[eventCode]
#
#     def getPidEvents(self, pid):
#         if pid not in self._pids:
#             return []
#         return self._pid2EventCodes[pid]


#
class SubscribeInfo:
    def __init__(self):
        self._contracts = None

    def getData(self):
        return [{"ContractNo":"CFFEX|F|IF|1905","KLineType":"Tick", "DataType":"OnTimeAssets"}]

    # def get


# 进程订阅了哪些合约
# 合约被哪些进程订阅
class SubscribeInfoMgr:
    def __init__(self):
        self._pids = set()
        self._pid2SubscribeInfos = {}
        #
        # ("DCE|F|I|1905", "OnTimeAssets", "Tick"): False
        self._state = {}

    # 插入请求合约，及参数信息
    def insert(self, pid, subscribeInfo):
        assert pid not in self._pids, "error"
        self._pids.add(pid)
        self._pid2SubscribeInfos[pid] = subscribeInfo
        for record in subscribeInfo.getData():
            key = (record["DataType"], record["KLineType"], record["ContractNo"])
            if key not in self._state:
                self._state[key] = False

    def getSubscriber(self, event):
        subscriber = []

        print(event.getDataType(), event.getKLineType(), event.getContractNo())
        for pid, subscibeInfo in self._pid2SubscribeInfos.items():
            for record in subscibeInfo.getData():
                print(record["DataType"], record["ContractNo"], record["KLineType"])
                if record["ContractNo"] == event.getContractNo() and record["DataType"] == event.getDataType()\
                and record["KLineType"] == event.getKLineType():
                    subscriber.append(pid)
        return subscriber

    # 交易和即时行情
    def getContracts_NoStop(self):
        if self._test:
            self._test = False
            return ["DCE|F|I|1905"]
        else:
            return []

    # 历史行情
    def getContracts_OnlyOnce(self):
        return []

    #
    def getZeroOberserveContracts(self):
        return []


# 上下文管理
class StrategyContext(object):
    def __init__(self, *args):
        self._config = None
        self._contracts = None
        self._i = None

    @property
    def contracts(self):
        return self._contracts

    @contracts.setter
    def contracts(self, value):
        self._contracts = value

    @property
    def i(self):
        return self._i

    @i.setter
    def i(self, value):
        self._i = value