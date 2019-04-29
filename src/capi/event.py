from capi.com_types import *
from .com_types import *

class Event:
    '''
    功能：api->引擎, 引擎->策略的消息
    格式：
        msg = 
        {
            'EventSrc'       , 事件来源, str
            'EventCode'      , 事件类型, int
            'ChainEnd'       , 是否有后续报文, str
            'ErrorCode'      , 错误码, int
            'ErrorText'      , 错误信息, str
            'Data'           , 事件消息体, list[dict]
            'DataFieldSize'  , 单个消息体大小, int
            'DataFieldCount' , 消息体个数, int
            'UserNo'         , 用户号, str
            'ContractNo'     , 合约号, str
            'KLineType'      , K线类型, str
            'KLineSlice'     , K线周期, int
            'SessionId'      , 会话号, int
        }
    '''
    def __init__(self, args):
        self._record = {}
        self._type = None
        if isinstance(args, dict):
            self._setDictArgs(args)
            self._type = ProcessEvent
        else:
            self._setClassArgs(args)
            self._type = CApiEvent
    
    def _setDictArgs(self, args):
        self._record = args
        
    def _setClassArgs(self, args):
        srvDict = self._record
        srvDict['EventSrc']       = chr(args.contents.SrvSrc)
        srvDict['EventCode']      = args.contents.SrvEvent
        srvDict['ChainEnd']       = chr(args.contents.SrvChain)
        srvDict['ErrorCode']      = args.contents.SrvErrorCode
        srvDict['ErrorText']      = args.contents.SrvErrorText.decode('utf-8')
        srvDict['Data']           = args.contents.SrvData
        srvDict['DataFieldSize']  = args.contents.DataFieldSize
        srvDict['DataFieldCount'] = args.contents.DataFieldCount
        srvDict['UserNo']         = args.contents.UserNo.decode('utf-8')
        srvDict['ContractNo']     = args.contents.ContractNo.decode('utf-8')
        srvDict['KLineType']      = args.contents.KLineType.decode('utf-8')
        srvDict['KLineSlice']     = args.contents.KLineSlice
        srvDict['SessionId']      = args.contents.SessionId
        
    def setData(self, data):
        self._record['Data'] = data
        
    def setStrategyId(self, id):
        self._record['StrategyId'] = id

    def setEventCode(self, eventCode):
        self._record["EventCode"] = eventCode

    def getStrategyId(self):
        return self._record['StrategyId']
  
    def getEventSrc(self):
        return self._record["EventSrc"]
        
    def getEventCode(self):
        return self._record["EventCode"]
        
    def getChain(self):
        return self._record["ChainEnd"]
        
    def getErrorCode(self):
        return self._record["ErrorCode"]
        
    def getErrorText(self):
        return self._record["ErrorText"]
        
    def getData(self):
        return self._record["Data"]
        
    def getFieldSize(self):
        return self._record['DataFieldSize']
        
    def getFieldCount(self):
        return self._record['DataFieldCount']
        
    def getUserNo(self):
        return self._record["UserNo"]

    def getContractNo(self):
        return self._record["ContractNo"]

    def getKLineType(self):
        return self._record["KLineType"]

    def getKLineSlice(self):
        return self._record["KLineSlice"]

    def isChainEnd(self):
        chain = self.getChain()
        if chain == EEQU_SRVCHAIN_END:
            return True
        return False
        
    def isSucceed(self):
        return self.getErrorCode() == 0

    def printTool(self):
        if self._type == ProcessEvent:
            print("Type：进程间事件",)
            print("EventCode: ", self._record["EventCode"])
            print("EventCode: ", self._record["EventCode"])
            print("StrategyId: ", self._record["StrategyId"])
            print("Data: ", self._record["Data"])
        elif self._type == CApiEvent:
            print("Type：C API 事件", )
            print("EventSrc: ", self._record["EventSrc"])
            print("EventCode: ", self._record["EventCode"])
            print("ContractNo: ", self._record["ContractNo"])
            print("SessionId: ", self._record["SessionId"])
            print("Data: ", self._record["Data"])

    def getEventType(self):
        return self._type

    def setESessionId(self, sessionId):
        self._record["ESessionId"] = sessionId

    def getESessionId(self):
        return self._record["ESessionId"]

    def getSessionId(self):
        return self._record["SessionId"]

    def setSessionI(self, sessionId):
        self._record['SessionId'] = sessionId

