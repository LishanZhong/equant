import os, time, math
from threading import Thread
from .com_types import *
from .event import *
from datetime import datetime

class PyAPI(object):
    '''与9.5交互api类，单例模式'''
        
    def __init__(self, logger, api2egQueue):
        self.logger = logger
        
        self._api2egQueue = api2egQueue
        
        # 注册回调事件
        self._regCallback()
        
        # 加载C Dll
        _dir = os.path.dirname(os.path.abspath(__file__))
        _cdllPath = os.path.join(_dir, "EQuantApi.dll")
        self._cDll = CDLL(_cdllPath)

        # 注册服务事件
        self._apiEventHandler = ServiceCallBackFuncType(self._apiCallbackFunc)
        self._cDll.E_RegEvent(self._apiEventHandler)
        
        # 初始化C Dll
        errorCode = self._cDll.E_Init()
        assert errorCode == 0, " C API init failed"

        # 策略编号<-->会话号
        self._SessionStrategyPair = {} #{session_id, strategy_id}
        # api session id : (strategy id , session id)
        self._apiSessionIdMap = { }

        # 统计相关结构定义
        self._CommodityList = []
        self._comContractDict = {}
        self._contractCount = 0
        self._exchangeCount = 0

        #

    def _setSessionId(self, session_id, strategy_id):
        self._SessionStrategyPair[session_id] = strategy_id
        
    def _getStrategyId(self, session_id):
        if session_id not in self._SessionStrategyPair:
            return 0
        return self._SessionStrategyPair[session_id]
        
    def _apiCallbackFunc(self, service):
        apiEvent = Event(service)
        code = apiEvent.getEventCode()
        if code not in self._apiCallbackDict:
            self.logger.error("callback(%d) not register!"%code)
            return -1
            
        self._apiCallbackDict[code](apiEvent)
        
        return 0
        
    def _regCallback(self):
        '''api回调事件处理函数'''
        self._apiCallbackDict = {
            EEQU_SRVEVENT_CONNECT           : self._onConnect        ,
            EEQU_SRVEVENT_DISCONNECT        : self._onDisconnect     ,
            EEQU_SRVEVENT_EXCHANGE          : self._onExchange       ,
            EEQU_SRVEVENT_COMMODITY         : self._onCommodity      ,
            EEQU_SRVEVENT_CONTRACT          : self._onCcontract      ,
            EEQU_SRVEVENT_QUOTESNAP         : self._onSnapshot       ,
            EEQU_SRVEVENT_QUOTESNAPLV2      : self._onDepthQuote     ,
            EEQU_SRVEVENT_HISQUOTEDATA      : self._onKlinedata      ,
            EEQU_SRVEVENT_HISQUOTENOTICE    : self._onKlinedata      ,
            EEQU_SRVEVENT_TIMEBUCKET        : self._onTimebucket     ,
            EEQU_SRVEVENT_TRADE_LOGINQRY    : self._onLoginInfo      ,
            EEQU_SRVEVENT_TRADE_USERQRY     : self._onUserInfo       ,
            EEQU_SRVEVENT_TRADE_LOGINNOTICE : self._onLoginInfo      ,
            EEQU_SRVEVENT_TRADE_ORDERQRY    : self._onOrderData      ,
            EEQU_SRVEVENT_TRADE_ORDER       : self._onOrderData      ,
            EEQU_SRVEVENT_TRADE_MATCHQRY    : self._onMatchData      ,
            EEQU_SRVEVENT_TRADE_MATCH       : self._onMatchData      ,
            EEQU_SRVEVENT_TRADE_POSITQRY    : self._onPositionData   ,
            EEQU_SRVEVENT_TRADE_POSITION    : self._onPositionData   ,
            EEQU_SRVEVENT_TRADE_FUNDQRY     : self._onMoney          ,
        } 
    #//////////////////////////初始化消息///////////////////////////
    
    def reqInit(self, event):
        '''初始化API'''
        ret = self._cDll.E_Init()
        if ret == 0:
            self.logger.info("Init C api successfully!")
        else:
            self.logger.info("Init C api failed, error code=%d"%ret)
        
    def reqDeInit(self, event):
        '''销毁API'''
        self._cDll.E_DeInit()
        
    #//////////////////////////行情请求消息/////////////////////////
    def reqExchange(self, event):
        '''
        功能：查询交易所
        参数：
            {
                'StrategyId': 策略id, int
                'Data' : 交易所编号 str
            }
        '''
        self.logger.debug('request exchange!')
        
        sessionId = c_uint()
        req = EEquExchangeReq(event.getData().encode())
        self._cDll.E_ReqQryExchangeInfo(byref(sessionId), byref(req))
        self._setSessionId(sessionId.value, event.getStrategyId())
        
    def reqCommodity(self, event):
        '''
        功能：查品种
        参数：
            {
                'StrategyId': 策略id, int
                'Data' : 起始品种编号 str
            }
        '''
        self.logger.debug('request commodity!')
        
        sessionId = c_uint()
        req = EEquCommodityReq(event.getData().encode())
        self._cDll.E_ReqQryCommodityInfo(byref(sessionId), byref(req))
        self._setSessionId(sessionId.value, event.getStrategyId())
        
    def reqContract(self, event):
        '''
        功能：查合约
        参数：
            {
                'StrategyId': 策略id, int
                'Data' : 起始合约编号 str
            }
        '''
        self.logger.debug('request contract!')
        
        sessionId = c_uint()
        req = EEquContractReq(event.getData().encode())
        self._cDll.E_ReqQryContractInfo(byref(sessionId), byref(req))
        self._setSessionId(sessionId.value, event.getStrategyId())
        
    def reqTimebucket(self, event):
        '''
        功能：查品种时间模板
        参数：
            {
                'StrategyId': 策略id, int
                'Data' : 品种编号 str
            }
        '''
        #self.logger.debug('request timebucket')
        if event.getData() == '':
            return
        
        sessionId = c_uint()
        req = EEquCommodityTimeBucketReq(event.getData().encode())
        self._cDll.E_ReqQryTimeBucketInfo(byref(sessionId), byref(req))
        self._setSessionId(sessionId.value, event.getStrategyId())
        
    def reqSubQuote(self, event):
        '''
        功能：订阅即时行情
        参数：
            {
                'StrategyId': 策略id, int
                'Data' : 合约列表 list
            }
        '''
        data = event.getData()
        self.logger.debug("request subscribe quote(%s)!"%(data))
        sessionId = c_uint()
        req = (c_char*101*len(data))()
        for i, contid in enumerate(data):
            memmove(addressof(req) + 101*i, contid.encode(), 101)
        self._cDll.E_ReqSubQuote(byref(sessionId), req, len(req))
        self._setSessionId(sessionId.value, event.getStrategyId())
        
    def reqUnsubQuote(self, event):
        '''
        功能：退订即时行情
        参数：
            {
                'StrategyId': 策略id, int
                'Data' : 合约列表 list
            }
        '''
        data = event.getData()
        self.logger.debug("request subscribe quote(%s)!"%(data))
        sessionId = c_uint()
        req = (c_char*101*len(data))()
        for i, contid in enumerate(data):
            memmove(addressof(req) + 101*i, contid.encode(), 101)
        self._cDll.E_ReqUnSubQuote(byref(sessionId), req, len(req))
        self._setSessionId(sessionId.value, event.getStrategyId())
        
    def reqSubHisquote(self, event):
        '''
        功能：订阅历史K线
        参数：
            {
                'StrategyId':策略id, int
                'Data': K线请求消息, dict
                    {
                        'ReqCount':请求数,int
                        'ContractNo':合约编号,str
                        'KLineType':K线类型,str
                        'KLineSlice':K线周期,int
                        'NeedNotice':订阅标志, str
                    }
            }
        '''
        self.logger.debug("%d request subscribe hisquote(%s)"%(event.getStrategyId(), event.getContractNo()))
        sessionId = c_uint()
        req = EEquKLineReq()
        data = event.getData()
        req.ReqCount = data['ReqCount']
        req.ContractNo = data['ContractNo'].encode()
        req.KLineType = data['KLineType'].encode()
        req.KLineSlice = data['KLineSlice']
        req.NeedNotice = data['NeedNotice'].encode()
        self._cDll.E_ReqSubHisQuote(byref(sessionId), byref(req))
        self._setSessionId(sessionId.value, event.getStrategyId())
        
    def reqUnsubHisquote(self, event):
        '''
        功能：退订历史K线
        参数：
            {
                'StrategyId':策略id, int 
                'Data':合约编号,str
            }
        '''
        data = event.getData()
        self.logger.debug("request unsubscribe hisquote(%s)"%event.getData())
        sessionId = c_uint()
        req = (c_char*101)()
        req = event.getData()
        self._cDll.E_ReqUnSubHisQuote(sessionId, req)
        self._setSessionId(sessionId.value, event.getStrategyId())
        
    def reqKLineStrategySwitch(self, event):
        '''
        功能：切换图表显示策略
        参数：
            {
                'StrategyId'    : 策略id，int,
                'Data'          : 
                    {
                        'StrategyName'  : 策略名称, str,
                        'ContractNo'    : 合约id，str
                        'KLineType'     : K线类型,str
                        'KLineSlice'    : K线周期，int   
                    }
            }
        '''
        sessionId = c_uint()
        req = EEquKLineStrategySwitch()
        data = event.getData()
        req.StrategyId = event.getStrategyId()
        req.StrategyName = data['StrategyName'].encode()
        req.ContractNo = data['ContractNo'].encode()
        req.KLineType = data['KLineType'].encode()
        req.KLineSlice = data['KLineSlice']
        self._cDll.E_KLineStrategySwitch(byref(sessionId), byref(req))
        self._setSessionId(sessionId.value, event.getStrategyId())
        
    def _getTickKLineData(self, dataList, cbuf):
        '''
        功能：创建C语言类型成交明细K线
        参数：
            dataList[
            {
                'KLineIndex'    : value,
                'TradeDate'     : value,
                'DateTimeStamp' : value,
                'TotalQty'      : value,
                'PositionQty'   : value,
                'LastPrice'     : value,
                'LastQty'       : value,
                'PositionChg'   : value,
                'BuyPrice'      : value,
                'SellPrice'     : value,
                'BuyQty'        : value,
                'SellQty'       : value,
            }]
        '''
        for i, d in enumerate(dataList):
            data = EEquKLineData()
            data.KLineIndex                                 = d['KLineIndex']
            data.TradeDate                                  = d['TradeDate']
            data.DateTimeStamp                              = d['DateTimeStamp']
            data.TotalQty                                   = d['TotalQty']
            data.PositionQty                                = d['PositionQty']
            data.LastPrice                                  = d['LastPrice']
            data.KLineData.KLineData1.LastQty               = d['LastQty']
            data.KLineData.KLineData1.PositionChg           = d['PositionChg']
            data.KLineData.KLineData1.BuyPrice              = d['BuyPrice']
            data.KLineData.KLineData1.SellPrice             = d['SellPrice']
            data.KLineData.KLineData1.BuyQty                = d['BuyQty']
            data.KLineData.KLineData1.SellQty               = d['SellQty']
            curBuf = cbuf + sizeof(EEquKLineData) * i
            cData = string_at(addressof(data), sizeof(EEquKLineData))
            memmove(curBuf, cData, sizeof(EEquKLineData))
        
    def _getMinuteKLineData(self, dataList, cbuf):
        '''
        功能：创建C语言类型日线和分钟线
        参数：
            dataList[
            {
                'KLineIndex'    : value,
                'TradeDate'     : value,
                'DateTimeStamp' : value,
                'TotalQty'      : value,
                'PositionQty'   : value,
                'LastPrice'     : value,
                'KLineQty'      : value,
                'OpeningPrice'  : value,
                'HighPrice'     : value,
                'LowPrice'      : value,
                'SettlePrice'   : value,
            }]
        '''
        for i, d in enumerate(dataList):
            data = EEquKLineData()
            data.KLineIndex                                  = d['KLineIndex']
            data.TradeDate                                   = d['TradeDate']
            data.DateTimeStamp                               = d['DateTimeStamp']
            data.TotalQty                                    = d['TotalQty']
            data.PositionQty                                 = d['PositionQty']
            data.LastPrice                                   = d['LastPrice']
            data.KLineData.KLineData0.KLineQty               = d['KLineQty']
            data.KLineData.KLineData0.OpeningPrice           = d['OpeningPrice']
            data.KLineData.KLineData0.HighPrice              = d['HighPrice']
            data.KLineData.KLineData0.LowPrice               = d['LowPrice']
            data.KLineData.KLineData0.SettlePrice            = d['SettlePrice']
            curBuf = cbuf + sizeof(EEquKLineData) * i
            cData = string_at(addressof(data), sizeof(EEquKLineData))
            memmove(curBuf, cData, sizeof(EEquKLineData))


    # N 批量发送，索引只能递增
    # U 单个发送，索引可以重复
    def sendKLineData(self, event, type):
        '''
        功能：推送或者推送回测K线数据
        参数：
            {
                'StrategyId'    : 策略id，int,
                'KLineType'     : K线类型，str
                'Data'          : {
                    'Count'     : K线数量
                    'Data'      : _getTickKLineData或者getMinuteKLineData
                }
            }
        '''
        # print("in py2c k line =============================")
        # print(datetime.now().strftime('%H:%M:%S.%f'))
        data = event.getData()
        sessionId = c_uint()
        
        bufSize = sizeof(EEquKLineData) * data['Count']
        pybuf = create_string_buffer(bufSize)
        cbuf = addressof(pybuf)
        
        if event.getKLineType() == EEQU_KLINE_TICK:
            self._getTickKLineData(data['Data'], cbuf)
        else:
            self._getMinuteKLineData(data['Data'], cbuf)
            
        req = EEquKLineDataResult()
        req.StrategyId = event.getStrategyId()
        req.Count = data['Count']
        req.Data = cast(cbuf, POINTER(EEquKLineData))
        
        if type == 'N':
            errorCode = self._cDll.E_KLineDataResult(byref(sessionId), byref(req))
        elif type == 'U':
            errorCode = self._cDll.E_KLineDataResultNotice(byref(sessionId), byref(req))
        self._setSessionId(sessionId.value, event.getStrategyId())

    # 增加指标线
    def addSeries(self, event):
        '''
        功能：增加指标线信息
        参数：
            {
                'StrategyId'    : 策略id，int,
                'Data'          :
                    {
                        'ItemName'  : 指标名称,str
                        'Type'      : 指标 类型,str
                        'Color'     : 颜色,int
                        'Thick'     : 线宽,int
                        'OwnAxis'   : 是否独立坐标,str
                        'Param'     : 参数
                            [
                                {
                                    ParamName  : 参数名,str
                                    ParamValue : 参数值,float
                                }
                                ...
                            ]
                        'ParamNum'  : 参数个数,int
                        'Groupid'   : 组号,str
                        'GroupName' : 组名,str
                        'Main'      : 主图、幅图
                    }
            }
        '''
        data = event.getData()
        sessionId = c_uint(0)
        _data = EEquKLineSeriesInfo()
        _data.ItemName = data['ItemName'].encode()  # 具体指标线 名称
        _data.Type = data['Type']                   # 线型
        _data.Color = data['Color']                 # 颜色
        _data.Thick = data['Thick']                 # 线宽
        # _data.OwnAxis = ord(data['OwnAxis'])      # 是否独立坐标
        # _data.Param = add                         # 参数 Max10 #
        _data.ParamNum = data['ParamNum']           # 参数个数
        _data.Groupid = data['Groupid']             # 组号
        _data.GroupName = data['GroupName'].encode()    # 组名（指标名）
        _data.Main = ord(data['Main'])              # 0 - 主图 1 - 副图1
        _data.StrategyId = event.getStrategyId()    # 策略ID
        errorCode = self._cDll.E_AddKLineSeriesInfo(byref(sessionId), byref(_data))
        assert errorCode == 0, "add kline series failed"
        self._setSessionId(sessionId.value, event.getStrategyId())

    def addSignal(self, event):
        '''
        功能：增加指标线信息
        参数：{
                'StrategyId'    : 策略id，int,
                'Data'          :
                    {
                        'ItemName'  : 指标名称,str
                        'Type'      : 指标 类型,str
                        'Color'     : 颜色,int
                        'Thick'     : 线宽,int
                        'OwnAxis'   : 是否独立坐标,str
                        'Param'     : 参数
                            [
                                {
                                    ParamName  : 参数名,str
                                    ParamValue : 参数值,float
                                }
                                ...
                            ]
                        'ParamNum'  : 参数个数,int
                        'Groupid'   : 组号,str
                        'GroupName' : 组名,str
                        'Main'      : 主图、幅图
                    }
            }
        '''
        data = event.getData()
        sessionId = c_uint(0)
        _data = EEquKLineSeriesInfo()
        _data.ItemName = data['ItemName'].encode()      # 具体指标线 名称
        _data.Type = data['Type']                       # 线型
        _data.Color = data['Color']                     # 颜色
        _data.Thick = data['Thick']                     # 线宽
        # _data.OwnAxis = ord(data['OwnAxis'])          # 是否独立坐标
        # _data.Param = add                             # 参数 Max10 #
        _data.ParamNum = data['ParamNum']               # 参数个数
        _data.Groupid = data['Groupid']                 # 组号
        _data.GroupName = data['GroupName'].encode()    # 组名（指标名）
        _data.Main = ord(data['Main'])                  # 0 - 主图 1 - 副图1
        _data.StrategyId = event.getStrategyId()        # 策略ID
        self._cDll.E_AddKLineSignalInfo(byref(sessionId), byref(_data))
        self._setSessionId(sessionId.value, event.getStrategyId())

    def _reqVertLineSeries(self, dataList, cbuf):
        '''
        功能：创建C语言类型的竖直线、变色线
        参数：
            dataList[
            {
                'KLineIndex'  : value,int
                'Value'       : value,float
                'ClrK'        : value,int
            }]
        '''
        
        for i, d in enumerate(dataList):
            data = EEquKLineSeries()
            data.KLineIndex  = d['KLineIndex']
            data.Value       = d['Value']
            data.ClrK        = d['ClrK']
            curBuf = cbuf + sizeof(EEquKLineSeries) * i
            cData = string_at(addressof(data), sizeof(EEquKLineSeries))
            memmove(curBuf, cData, sizeof(EEquKLineSeries))
            
    def _reqIndicatorSeries(self, dataList, cbuf):
        '''
        功能：创建C语言类型的指标线
        参数：
            dataList[
            {
                'KLineIndex'  : value,int
                'Value'       : value,float
            }]
        '''
        
        for i, d in enumerate(dataList):
            data = EEquKLineSeries()
            data.KLineIndex  = d['KLineIndex']
            data.Value       = d['Value']
            curBuf = cbuf + sizeof(EEquKLineSeries) * i
            cData = string_at(addressof(data), sizeof(EEquKLineSeries))
            memmove(curBuf, cData, sizeof(EEquKLineSeries))
            
    def _reqBarSeries(self, dataList, cbuf):
        '''
        功能：创建C语言类型的柱子
        参数：
            dataList[
            {
                'KLineIndex'  : value, int
                'Value'       : value, float
                'ClrBar'      : value, int
                'Filled'      : value, str
                'BarValue'    : value, flaot
            }]
        '''
        
        for i, d in enumerate(dataList):
            data = EEquKLineSeries()
            data.KLineIndex  = d['KLineIndex']
            data.Value       = d['Value']
            data.ClrK        = d['ClrK']
            data.ClrBar      = d['ClrBar']
            data.Filled      = d['Filled'].encode()
            data.BarValue    = d['BarValue']
            curBuf = cbuf + sizeof(EEquKLineSeries) * i
            cData = string_at(addressof(data), sizeof(EEquKLineSeries))
            memmove(curBuf, cData, sizeof(EEquKLineSeries))

    def _reqDotSeries(self, dataList, cbuf):
        '''
        功能：创建C语言类型的图标、点指标
        参数：
            dataList[
            {
                'KLineIndex'  : value, int
                'Value'       : value, float
                'Icon'        : value, int
            }]
        '''
        
        for i, d in enumerate(dataList):
            data = EEquKLineSeries()
            data.KLineIndex  = d['KLineIndex']
            data.Value       = d['Value']
            data.Icon        = d['Icon']
            curBuf = cbuf + sizeof(EEquKLineSeries) * i
            cData = string_at(addressof(data), sizeof(EEquKLineSeries))
            memmove(curBuf, cData, sizeof(EEquKLineSeries)) 
     
    def _reqStickLineSeries(self, dataList, cbuf):
        '''
        功能：创建C语言类型的竖线段指标
        参数：
            dataList[
            {
                'KLineIndex'  : value, int
                'Value'       : value, float
                'ClrStick'    : value, int
                'StickValue'  : value, float
            }]
        '''
        
        for i, d in enumerate(dataList):
            data = EEquKLineSeries()
            data.KLineIndex  = d['KLineIndex']
            data.Value       = d['Value']
            data.ClrStick    = d['ClrStick']
            data.StickValue  = d['StickValue']
            curBuf = cbuf + sizeof(EEquKLineSeries) * i
            cData = string_at(addressof(data), sizeof(EEquKLineSeries))
            memmove(curBuf, cData, sizeof(EEquKLineSeries)) 
             
    def _reqPartLineSeries(self, dataList, cbuf):
        '''
        功能：创建C语言类型的线段
        参数：
            dataList[
            {
                'KLineIndex'  : value, int
                'Value'       : value, float
                'Idx2'        : value, int
                'ClrLine'     : value, int
                'LineValue'   : value, float
                'LinWid'      : value, float
            }]
        '''
        
        for i, d in enumerate(dataList):
            data = EEquKLineSeries()
            data.KLineIndex  = d['KLineIndex']
            data.Value       = d['Value']
            data.Idx2        = d['Idx2']
            data.ClrLine     = d['ClrLine']
            data.LineValue   = d['LineValue']
            data.LinWid      = d['LinWid']
            curBuf = cbuf + sizeof(EEquKLineSeries) * i
            cData = string_at(addressof(data), sizeof(EEquKLineSeries))
            memmove(curBuf, cData, sizeof(EEquKLineSeries)) 

    # N，批量发送数据，k线索引只能递增
    # U，单个发送数据，k线索引可以重复
    def sendKLineSeries(self, event, type):
        '''
        功能：推送或更新回测指标数据
        参数：
            {
                'StrategyId'    : 策略id，int,
                'Data'          :
                    {
                        'SeriesName'  : 指标名称,str
                        'SeriesType'  : 指标类型,str
                        'IsMain'      : 是否主副图,str
                        'Count'       : 指标数量
                        'Data'        : 参数
                            [
                                _reqVertLineSeries   变色K线、竖直直线
                                _reqIndicatorSeries  指标线
                                _reqBarSeries        柱子
                                _reqDotSeries        图标、点
                                _reqStickLineSeries  竖线段
                                _reqPartLineSeries   线段
                            ]
                    }
            }
        '''

        data = event.getData()
        sessionId = c_uint(0)
        bufSize = sizeof(EEquKLineSeries) * data['Count']
        pybuf = create_string_buffer(bufSize)
        cbuf = addressof(pybuf)

        seriesType = data['SeriesType']
        if seriesType == EEQU_VERTLINE:                     # 竖直直线
            self._reqVertLineSeries(data['Data'], cbuf)
        elif seriesType == EEQU_BAR:                        # 柱子
            self._reqBarSeries(data['Data'], cbuf)
        elif seriesType == EEQU_STICKLINE:                  # 竖线段
            self._reqStickLineSeries(data['Data'], cbuf)
        elif seriesType == EEQU_COLORK:                     # 变色K线
            self._reqVertLineSeries(data['Data'], cbuf)
        elif seriesType == EEQU_PARTLINE:                   # 线段
            self._reqPartLineSeries(data['Data'], cbuf)
        elif seriesType == EEQU_ICON:                       # 图标
            self._reqDotSeries(data['Data'], cbuf)
        elif seriesType == EEQU_DOT:                        # 点
            self._reqDotSeries(data['Data'], cbuf)
        else:
            self._reqIndicatorSeries(data['Data'], cbuf)

        req = EEquKLineSeriesResult()
        req.StrategyId = event.getStrategyId()
        req.SeriesName = data['SeriesName'].encode()
        req.SeriesType = data['SeriesType']
        req.IsMain = ord(data['IsMain'])
        req.Count = data['Count']
        req.Data = cast(cbuf, POINTER(EEquKLineSeries))

        if type == 'N':
            self._cDll.E_KLineSeriesResult(byref(sessionId), byref(req))
        elif type == 'U':
            self._cDll.E_KLineSeriesResultNotice(byref(sessionId), byref(req))
        self._setSessionId(sessionId.value, event.getStrategyId())


    # N,批量发送，索引只能递增。
    # U,单个发送，索引可以重复。
    def sendKLineSignal(self, event, type):
        '''
        功能：推送或更新回测指标数据
        参数：
            {
                'StrategyId'    : 策略id，int,
                'Data'          : 
                    {
                        'SeriesName'  : 指标名称,str
                        'Count'       : 指标数量
                        'Data'        : 参数
                            [
                                {
                                    'KLineIndex' : K线索引,int
                                    'ContractNo' : 合约
                                    'Direct'     : 买卖方向,str
                                    'Offset'     : 开平,str
                                    'Price'      : 价格,float
                                    'Qty'        : 数量,int
                                }
                            ]
                    }
            }
        '''
        data = event.getData()
        sessionId = c_uint(0)

        bufSize = sizeof(EEquSignalItem) * data['Count']
        pybuf = create_string_buffer(bufSize)
        cbuf = addressof(pybuf)

        for i, d in enumerate(data['Data']):
            eEquSignalItem = EEquSignalItem()
            eEquSignalItem.KLineIndex = d['KLineIndex']
            eEquSignalItem.ContractNo = d['ContractNo'].encode()
            eEquSignalItem.Direct = d['Direct'].encode()
            eEquSignalItem.Offset = d['Offset'].encode()
            eEquSignalItem.Price = d['Price']
            eEquSignalItem.Qty = d['Qty']
            curBuf = cbuf + sizeof(EEquSignalItem) * i
            cData = string_at(addressof(eEquSignalItem), sizeof(EEquSignalItem))
            memmove(curBuf, cData, sizeof(EEquSignalItem))

        req = EEquKLineSignalResult()
        req.StrategyId = event.getStrategyId()
        req.SeriesName = data['SeriesName'].encode()
        req.Count = data['Count']
        req.Data = cast(cbuf, POINTER(EEquSignalItem))

        if type == 'N':
            self._cDll.E_KLineSignalResult(byref(sessionId), byref(req))
        elif type == 'U':
            self._cDll.E_KLineSignalResultNotice(byref(sessionId), byref(req))
        self._setSessionId(sessionId.value, event.getStrategyId())

    def reqStrategyDataUpdateNotice(self, event):
        '''
        功能：刷新指标、信号通知
        参数：
            {
                'StrategyId'    : 策略id，int,
            }
        '''
        sessionId = c_uint()
        req = EEquStrategyDataUpdateNotice()
        req.StrategyId = event.getStrategyId()
        self._cDll.E_StrategyDataUpdateNotice(byref(sessionId), byref(req))
        self._setSessionId(sessionId.value, event.getStrategyId())
        
    #////////////////////////////交易数据请求///////////////////////
    def reqQryLoginInfo(self, event):
        '''
        功能：查询登录账户信息
        参数：
            {
                'Data': 为空
                {
                    'LoginNo' : 登录账号,str
                    'Sign'    : 服务器标识,str
                }
            }
        '''
        self.logger.info("Request query login info:%s"%event.getData())
        sessionId = c_uint()
        req = EEquLoginInfoReq()
        self._cDll.E_ReqQryLoginInfo(byref(sessionId), byref(req))
        
    def reqQryUserInfo(self, event):
        '''
        功能：查询资金账号
        参数：
            {
                'Data': 为空
                {
                    'UserNo'  : 登录账号,str
                    'Sign'    : 服务器标识,str
                }
            }
        '''
        self.logger.info("Request query user info:%s"%event.getData())
        sessionId = c_uint()
        req = EEquUserInfoReq()
        self._cDll.E_ReqQryUserInfo(byref(sessionId), byref(req))
        
    def reqQryMoney(self, event):
        '''
        功能：查询资金账号
        参数：
            {
                'Data':
                {
                    'UserNo'     : 登录账号,str
                    'Sign'       : 服务器标识,str
                    'CurrencyNo' : 币种,Currency_Base查询基币
                }
            }
        '''
        self.logger.info("Request query money:%s"%event.getData())
        sessionId = c_uint()
        data = event.getData()
        req = EEquUserMoneyReq()
        req.UserNo = data['UserNo'].encode()
        req.Sign = data['Sign'].encode()
        req.CurrencyNo = data['CurrencyNo'].encode()
        self._cDll.E_ReqQryMoney(byref(sessionId), byref(req))
        
    def reqQryOrder(self, event):
        '''
        功能：查询委托信息
        参数：
            {
                'StrategyId'  :  策略编号
                'Data'        :  数据
                    {
                        'UserNo'     : 登录账号,str
                        'Sign'       : 服务器标识,str
                    }
            }
        '''
        sessionId = c_uint()
        data = event.getData()
        self.logger.debug('Request query order:%s'%event.getData())
        req = EEquOrderQryReq()
        req.UserNo = data['UserNo'].encode()
        req.Signa = data['Sign'].encode()
        self._cDll.E_ReqQryOrder(byref(sessionId), byref(req))
        self._setSessionId(sessionId.value, event.getStrategyId())
        
        
    def reqQryMatch(self, event):
        '''查询成交信息'''
        sessionId = c_uint()
        data = event.getData()
        self.logger.debug('Request query match:%s'%event.getData())
        req = EEquOrderQryReq()
        req.UserNo = data['UserNo'].encode()
        req.Signa = data['Sign'].encode()
        self._cDll.E_ReqQryMatch(byref(sessionId), byref(req))
        self._setSessionId(sessionId.value, event.getStrategyId())
        
    def reqQryPosition(self, event):
        '''查询持仓信息'''
        sessionId = c_uint()
        data = event.getData()
        self.logger.debug('Request query position:%s'%event.getData())
        req = EEquOrderQryReq()
        req.UserNo = data['UserNo'].encode()
        req.Signa = data['Sign'].encode()
        self._cDll.E_ReqQryPosition(byref(sessionId), byref(req))
        self._setSessionId(sessionId.value, event.getStrategyId())

    # 委托下单
    def reqInsertOrder(self, event):
        '''
        功能：下单
        参数：
            {
                'Data':
                {
                    'UserNo'           : 登录账号,str
                    'Sign'             : 服务器标识,str
                    'Cont'             : 行情合约,str
                    'OrderType'        : 定单类型,str
                    'ValidType'        : 有效类型,str
                    'ValidTime'        : 有效时间,str
                    'Direct'           : 买卖方向,str
                    'Offset'           : 开平方式,str
                    'Hedge'            : 投机套保,str
                    'OrderPrice'       : 委托价格,float
                    'TriggerPrice'     : 触发价格,float
                    'TriggerMode'      : 触发模式,str
                    'TriggerCondition' : 触发条件,str
                    'OrderQty'         : 委托数量,int
                    'StrategyType'     : 策略类型,str
                    'Remark'           : 下单备注字段,str
                    'AddOneIsValid'    : T+1时段有效(仅港交所)
                }
            }
        '''
        sessionId = c_uint()
        data = event.getData()
        req = EEquOrderInsertReq()
        req.UserNo = data['UserNo'].encode()
        req.Sign = data['Sign'].encode()
        req.Cont = data['Cont'].encode()
        req.OrderType = data['OrderType'].encode()
        req.ValidType = data['ValidType'].encode()
        req.ValidTime = data['ValidTime'].encode()
        req.Direct = data['Direct'].encode()
        req.Offset = data['Offset'].encode()
        req.Hedge = data['Hedge'].encode()
        req.OrderPrice = data['OrderPrice']
        req.TriggerPrice = data['TriggerPrice']
        req.TriggerMode = data['TriggerMode'].encode()
        req.TriggerCondition = data['TriggerCondition'].encode()
        req.OrderQty = data['OrderQty']
        req.StrategyType = data['StrategyType'].encode()
        req.Remark = data['Remark'].encode()
        req.AddOneIsValid = data['AddOneIsValid'].encode()
        self._cDll.E_ReqInsertOrder(byref(sessionId), byref(req))

        self._apiSessionIdMap[sessionId.value] = (event.getStrategyId(), event.getESessionId())

        sessionIdMapEvent = Event({
            "EventCode":EV_EG2ST_ACTUAL_ORDER_SESSION_MAP,
            "StrategyId":event.getStrategyId(),
            "ESessionId":event.getESessionId(),
            "SessionId":sessionId.value,
        })
        self._api2egQueue.put(sessionIdMapEvent)

    def reqCancelOrder(self, event):
        '''
        功能：撤单
        参数：
            {
                'Data':
                {
                    'OrderId'           : 合约编号,int
                }
            }
        '''
        sessionId = c_uint()
        data = event.getData()
        cancelReq = EEquOrderCancelReq()
        cancelReq.OrderId = data['OrderId']
        self._cDll.E_ReqCancelOrder(byref(sessionId), byref(cancelReq))
        
    def reqModifyOrder(self, event):
        '''改单'''
        sessionId = c_uint()
        data = event.getData()
        modifyReq = EEquOrderModifyReq()
        modifyReq.UserNo = data['UserNo'].encode()
        modifyReq.Sign = data['Sign'].encode()
        modifyReq.Cont = data['Cont'].encode()
        modifyReq.OrderType = data['OrderType'].encode()
        modifyReq.ValidType = data['ValidType'].encode()
        modifyReq.ValidTime = data['ValidTime'].encode()
        modifyReq.Direct = data['Direct'].encode()
        modifyReq.Offset = data['Offset'].encode()
        modifyReq.Hedge = data['Hedge'].encode()
        modifyReq.OrderPrice = data['OrderPrice']
        modifyReq.TriggerPrice = data['TriggerPrice']
        modifyReq.TriggerMode = data['TriggerMode'].encode()
        modifyReq.TriggerCondition = data['TriggerCondition'].encode()
        modifyReq.OrderQty = data['OrderQty']
        modifyReq.StrategyType = data['StrategyType'].encode()
        modifyReq.Remark = data['Remark'].encode()
        modifyReq.AddOneIsValid = data['AddOneIsValid'].encode()
        modifyReq.OrderId = data['OrderId']
        self._cDll.E_ReqModifyOrder(byref(sessionId), byref(modifyReq))
    
    #////////////////////////////回调消息/////////////////////////// 
    def _onConnect(self, apiEvent):
        if apiEvent.getErrorCode() != 0:
            self.logger.error('Connect epolestar 9.5 error!')
            return
        
        self.logger.info('Connect epolestar 9.5 successfully!')
        apiEvent.setData('')
        sid = apiEvent.getSessionId()
        apiEvent.setStrategyId(self._getStrategyId(sid))
        self._api2egQueue.put(apiEvent)
        
    def _onDisconnect(self, apiEvent):
        self.logger.error('Disconnect to epolestar 9.5!')
        apiEvent.setData('')
        sid = apiEvent.getSessionId()
        apiEvent.setStrategyId(self._getStrategyId(sid))
        self._api2egQueue.put(apiEvent)
        
        
    def _onExchange(self, apiEvent):
        '''交易所数据应答'''
        dataAddr   = apiEvent.getData()
        fieldSize  = apiEvent.getFieldSize()
        fieldCount = apiEvent.getFieldCount()
        
        dataList = []
        
        for i in range(fieldCount):
            buf = string_at(dataAddr + fieldSize * i, fieldSize)
            data = EEquExchangeData()
            memmove(addressof(data), buf, sizeof(EEquExchangeData))
            
            idict = {
                'ExchangeNo'    : data.ExchangeNo.decode('utf-8'),
                'ExchangeName'  : data.ExchangeName.decode('utf-8')
            }
            dataList.append(idict)
            self._exchangeCount += 1
        
        #发送到引擎  
        apiEvent.setData(dataList)
        sid = apiEvent.getSessionId()
        apiEvent.setStrategyId(self._getStrategyId(sid))
        self._api2egQueue.put(apiEvent)
        
        # 交易数据已经完了，查品种数据吧
        if apiEvent.isChainEnd():
            self.logger.info("request exchage data over(%d)!"%(self._exchangeCount))
        else: 
            pass

    def _onCommodity(self, apiEvent):
        '''品种数据应答'''
        dataAddr   = apiEvent.getData()
        fieldSize  = apiEvent.getFieldSize()
        fieldCount = apiEvent.getFieldCount()
        
        dataList = []
        
        for i in range(fieldCount):
            buf = string_at(dataAddr + fieldSize * i, fieldSize)
            data = EEquCommodityData()
            memmove(addressof(data), buf, sizeof(EEquCommodityData))
            
            idict = {
                'ExchangeNo'     : data.ExchangeNo.decode('utf-8'),
                'CommodityNo'    : data.CommodityNo.decode('utf-8'),
                'CommodityType'  : data.CommodityType.decode('utf-8'),
                'CommodityName'  : data.CommodityName.decode('utf-8'),
                'PriceNume'      : data.PriceNume,
                'PriceDeno'      : data.PriceDeno,
                'PriceTick'      : data.PriceTick,
                'PricePrec'      : data.PricePrec,
                'TradeDot'       : data.TradeDot,
                'CoverMode'      : data.CoverMode.decode('utf-8'),
            }
            
            dataList.append(idict)
            
            # api保存品种信息，查模板使用 
            self._CommodityList.append(idict['CommodityNo'])
            self._comContractDict[idict['CommodityNo']] = []
        
        #发送到引擎  
        apiEvent.setData(dataList)
        sid = apiEvent.getSessionId()
        apiEvent.setStrategyId(self._getStrategyId(sid))
        self._api2egQueue.put(apiEvent)
        
        # 查合约
        if apiEvent.isChainEnd():
            self.logger.info("request commodity data over(%d)!"%(len(self._CommodityList)))
        else:
            pass
            
    def _onCcontract(self, apiEvent):
        '''合约数据应答'''
        dataAddr   = apiEvent.getData()
        fieldSize  = apiEvent.getFieldSize()
        fieldCount = apiEvent.getFieldCount()
        
        dataList = []
        
        for i in range(fieldCount):
            buf = string_at(dataAddr + fieldSize * i, fieldSize)
            data = EEquContractData()
            memmove(addressof(data), buf, sizeof(EEquContractData))
            
            idict = {
                'ExchangeNo'  : data.ExchangeNo.decode('utf-8'),
                'CommodityNo' : data.CommodityNo.decode('utf-8'),
                'ContractNo'  : data.ContractNo.decode('utf-8'),
            }
           
            dataList.append(idict)
            self._contractCount += 1
            self._comContractDict[idict['CommodityNo']].append(idict['ContractNo'])
        
        #发送到引擎  
        apiEvent.setData(dataList)
        sid = apiEvent.getSessionId()
        apiEvent.setStrategyId(self._getStrategyId(sid))
        self._api2egQueue.put(apiEvent)
        
        if apiEvent.isChainEnd():
            self.logger.info("request contract data over(%d)!"%(self._contractCount))
        else:
            pass
            
            
    def _onSnapshot(self, apiEvent):
        '''即时行情应答'''
        dataAddr   = apiEvent.getData()
        fieldSize  = apiEvent.getFieldSize()
        fieldCount = apiEvent.getFieldCount()
        
        dataList = []
        for i in range(fieldCount):
            # 1. 解析SnapShotData
            snapBuf = string_at(dataAddr + fieldSize * i, fieldSize)
            fieldData = EEquSnapShotData()
            memmove(addressof(fieldData), snapBuf, sizeof(EEquSnapShotData))
            
            fieldDataDict = {
                'UpdateTime' : fieldData.UpdateTime,
                'FieldCount' : fieldData.FieldCount,
            }
            
            
            fieldDict = {}
            for j in range(fieldDataDict['FieldCount']):
                fieldAddr = dataAddr + sizeof(c_ulonglong) + sizeof(c_ubyte)
                fieldBuf = string_at(fieldAddr + sizeof(EEquQuoteField)*j, sizeof(EEquQuoteField))
                field = EEquQuoteField()
                memmove(addressof(field), fieldBuf, sizeof(EEquQuoteField))
                
                fidValue = None
                fidMean = field.QuoteFieldUnion0.FidMean
                fieldType = EEQU_FIDTYPE_ARRAY[fidMean]
                
                if fieldType == EEQU_FIDTYPE_PRICE:
                    fidValue = field.QuoteFieldUnion1.Price      
                elif fieldType == EEQU_FIDTYPE_QTY:
                    fidValue = field.QuoteFieldUnion1.Qty
                else:
                    pass
                    
                fieldDict[fidMean] = fidValue
            
            fieldDataDict['FieldData'] = fieldDict
            
            dataList.append(fieldDataDict)
        
        # 发送到引擎
        apiEvent.setData(dataList)
        sid = apiEvent.getSessionId()
        apiEvent.setStrategyId(self._getStrategyId(sid))
        self._api2egQueue.put(apiEvent)
            
    def _onDepthQuote(self, apiEvent):
        '''深度行情'''
        dataAddr   = apiEvent.getData()
        fieldSize  = apiEvent.getFieldSize()
        fieldCount = apiEvent.getFieldCount()
        
        dataList = []
        
        for i in range(fieldCount):
            buf = string_at(dataAddr + fieldSize * i, fieldSize)
            data = EEquQuoteSnapShotL2()
            memmove(addressof(data), buf, sizeof(EEquQuoteSnapShotL2))
            
            l2Dict = {}
            bidList,askList = [],[]
            
            for j in range(EEQU_MAX_L2_DEPTH):
                if math.isclose(data.BidQuoteFieldL2[j].Price, 0.0):
                    break
                    
                bidDict = {
                    'Price'  :  data.BidQuoteFieldL2[j].Price,
                    'Qty'    :  data.BidQuoteFieldL2[j].Qty
                }
                bidList.append(bidDict)
            
            for j in range(EEQU_MAX_L2_DEPTH):
                if math.isclose(data.BidQuoteFieldL2[j].Price, 0.0):
                    break
            
                askDict = {
                    'Price'  :  data.AskQuoteFieldL2[j].Price,
                    'Qty'    :  data.AskQuoteFieldL2[j].Qty
                }
                askList.append(askDict)
                
            l2Dict['Bid'] = bidList
            l2Dict['Ask'] = askList
            
            dataList.append(l2Dict)
        
        # 发送到引擎
        apiEvent.setData(dataList)
        sid = apiEvent.getSessionId()
        apiEvent.setStrategyId(self._getStrategyId(sid))
        self._api2egQueue.put(apiEvent)
        
    def _onTimebucket(self, apiEvent):
        dataAddr   = apiEvent.getData()
        fieldSize  = apiEvent.getFieldSize()
        fieldCount = apiEvent.getFieldCount()
        
        dataList = []
        
        for i in range(fieldCount):
            buf = string_at(dataAddr + fieldSize * i, fieldSize)
            data = EEquHisQuoteTimeBucket()
            memmove(addressof(data), buf, sizeof(EEquHisQuoteTimeBucket))
            
            idict = {
                'Index'     : data.Index,
                'BeginTime' : data.BeginTime,
                'EndTime'   : data.EndTime,
                'TradeState': data.TradeState.decode('utf-8'),
                'DateFlag'  : data.DateFlag.decode('utf-8'),
                'CalCount'  : data.CalCount,
                'Commodity' : data.Commodity.decode('utf-8')
            }           
            
            dataList.append(idict)
        
        # 发送到引擎
        apiEvent.setData(dataList)
        sid = apiEvent.getSessionId()
        apiEvent.setStrategyId(self._getStrategyId(sid))
        self._api2egQueue.put(apiEvent)
        
    def _onKlinedata(self, apiEvent):
        dataAddr   = apiEvent.getData()
        fieldSize  = apiEvent.getFieldSize()
        fieldCount = apiEvent.getFieldCount()
        klineType  = apiEvent.getKLineType()
        
        dataList = []
        
        for i in range(fieldCount):
            buf = string_at(dataAddr + fieldSize * i, fieldSize)
            data = EEquKLineData()
            memmove(addressof(data), buf, sizeof(EEquKLineData))
            
            idict = {
                'KLineIndex'    : data.KLineIndex,
                'TradeDate'     : data.TradeDate,
                'DateTimeStamp' : data.DateTimeStamp,
                'TotalQty'      : data.TotalQty,
                'PositionQty'   : data.PositionQty,
                'LastPrice'     : data.LastPrice
            }
            
            if klineType == EEQU_KLINE_TICK:
                idict['LastQty']      = data.KLineData.KLineData1.LastQty
                idict['PositionChg']  = data.KLineData.KLineData1.PositionChg
                idict['BuyPrice']     = data.KLineData.KLineData1.BuyPrice
                idict['SellPrice']    = data.KLineData.KLineData1.SellPrice
                idict['BuyQty']       = data.KLineData.KLineData1.BuyQty
                idict['SellQty']      = data.KLineData.KLineData1.SellQty
                
            else:
                idict['KLineQty']     = data.KLineData.KLineData0.KLineQty
                idict['OpeningPrice'] = data.KLineData.KLineData0.OpeningPrice
                idict['HighPrice']    = data.KLineData.KLineData0.HighPrice
                idict['LowPrice']     = data.KLineData.KLineData0.LowPrice
                idict['SettlePrice']  = data.KLineData.KLineData0.SettlePrice
            
            dataList.append(idict)
        
        # 发送到引擎
        apiEvent.setData(dataList)
        sid = apiEvent.getSessionId()
        apiEvent.setStrategyId(self._getStrategyId(sid))
        self._api2egQueue.put(apiEvent)
        
        
    def _onLoginInfo(self, apiEvent):
        '''登录账号应答'''
        dataAddr   = apiEvent.getData()
        fieldSize  = apiEvent.getFieldSize()
        fieldCount = apiEvent.getFieldCount()
        
        dataList = []
        
        for i in range(fieldCount):
            buf = string_at(dataAddr + fieldSize * i, fieldSize)
            data = EEquLoginInfoRsp()
            memmove(addressof(data), buf, sizeof(EEquLoginInfoRsp))
            
            idict = {
                'LoginNo'   : data.LoginNo.decode('utf-8'),
                'Sign'      : data.Sign.decode('utf-8'),
                'LoginName' : data.LoginName.decode('utf-8'),
                'LoginApi'  : data.LoginApi.decode('utf-8'),
                'TradeDate' : data.TradeDate.decode('utf-8'),
                'IsReady'   : data.IsReady.decode('utf-8'),
            }
            dataList.append(idict)
        
        # print(dataList)
        # 发送到引擎
        apiEvent.setData(dataList)
        self._api2egQueue.put(apiEvent)
        
    def _onUserInfo(self, apiEvent):
        '''登录账号应答'''
        dataAddr   = apiEvent.getData()
        fieldSize  = apiEvent.getFieldSize()
        fieldCount = apiEvent.getFieldCount()
        
        dataList = []
        
        for i in range(fieldCount):
            buf = string_at(dataAddr + fieldSize * i, fieldSize)
            data = EEquUserInfoRsp()
            memmove(addressof(data), buf, sizeof(EEquUserInfoRsp))
            
            idict = {
                'UserNo'    : data.UserNo.decode('utf-8'),
                'Sign'      : data.Sign.decode('utf-8'),
                'LoginNo'   : data.LoginNo.decode('utf-8'),
                'UserName'  : data.UserName.decode('utf-8')
            }
            dataList.append(idict)
        
        # print(dataList)
        # 发送到引擎
        apiEvent.setData(dataList)
        self._api2egQueue.put(apiEvent)

    def _onOrderData(self, apiEvent):
        '''委托通知'''
        dataAddr   = apiEvent.getData()
        fieldSize  = apiEvent.getFieldSize()
        fieldCount = apiEvent.getFieldCount()
        
        dataList = []
        
        for i in range(fieldCount):
            buf = string_at(dataAddr + fieldSize * i, fieldSize)
            data = EEquOrderDataNotice()
            memmove(addressof(data), buf, sizeof(EEquOrderDataNotice))
            
            idict = {
                'SessionId'        : data.SessionId,
                'UserNo'           : data.UserNo.decode('utf-8'),
                'Sign'             : data.Sign.decode('utf-8'),
                'Cont'             : data.Cont.decode('utf-8'),
                'OrderType'        : data.OrderType.decode('utf-8'),
                'ValidType'        : data.ValidType.decode('utf-8'),
                'ValidTime'        : data.ValidTime.decode('utf-8'),
                'Direct'           : data.Direct.decode('utf-8'),
                'Offset'           : data.Offset.decode('utf-8'),
                'Hedge'            : data.Hedge.decode('utf-8'),
                'OrderPrice'       : data.OrderPrice,
                'TriggerPrice'     : data.TriggerPrice,
                'TriggerMode'      : data.TriggerMode.decode('utf-8'),
                'TriggerCondition' : data.TriggerCondition.decode('utf-8'),
                'OrderQty'         : data.OrderQty,
                'StrategyType'     : data.StrategyType.decode('utf-8'),
                'Remark'           : data.Remark.decode('utf-8'),
                'AddOneIsValid'    : data.AddOneIsValid.decode('utf-8'),
                'OrderState'       : data.OrderState.decode('utf-8'),
                'OrderId'          : data.OrderId,
                'OrderNo'          : data.OrderNo.decode('utf-8'),
                'MatchPrice'       : data.MatchPrice,
                'MatchQty'         : data.MatchQty,
                'ErrorCode'        : data.ErrorCode,
                'ErrorText'        : data.ErrorText.decode('gbk'),
                'InsertTime'       : data.InsertTime.decode('utf-8'),
                'UpdateTime'       : data.UpdateTime.decode('utf-8'),
            }
            dataList.append(idict)
        
        # 发送到引擎
        apiEvent.setData(dataList)
        sid = apiEvent.getSessionId()

        # print( " now api session id is ", sid)
        # print(self._apiSessionIdMap, self._SessionStrategyPair)
        # print(apiEvent.getData())
        apiEvent.setStrategyId(self._getStrategyId(sid))
        if sid in self._apiSessionIdMap:
            apiEvent.setESessionId(self._apiSessionIdMap[sid][1])
        self._api2egQueue.put(apiEvent)

    def _onMatchData(self, apiEvent):
        '''成交通知'''
        dataAddr   = apiEvent.getData()
        fieldSize  = apiEvent.getFieldSize()
        fieldCount = apiEvent.getFieldCount()
        
        dataList = []
        
        for i in range(fieldCount):
            buf = string_at(dataAddr + fieldSize * i, fieldSize)
            data = EEquMatchNotice()
            memmove(addressof(data), buf, sizeof(EEquMatchNotice))
            
            idict = {
                'UserNo'           : data.UserNo.decode('utf-8'),
                'Sign'             : data.Sign.decode('utf-8'),
                'Cont'             : data.Cont.decode('utf-8'),
                'Direct'           : data.Direct.decode('utf-8'),
                'Offset'           : data.Offset.decode('utf-8'),
                'Hedge'            : data.Hedge.decode('utf-8'),
                'OrderNo'          : data.OrderNo.decode('utf-8'),
                'MatchPrice'       : data.MatchPrice,
                'MatchQty'         : data.MatchQty,
                'FeeCurrency'      : data.FeeCurrency.decode('utf-8'),
                'MatchFee'         : data.MatchFee,
                'MatchDateTime'    : data.MatchDateTime.decode('utf-8'),
                'AddOne'           : data.AddOne.decode('utf-8'),
                'Deleted'          : data.Deleted.decode('utf-8'),
            }
            dataList.append(idict)
        
        # 发送到引擎
        apiEvent.setData(dataList)
        sid = apiEvent.getSessionId()
        apiEvent.setStrategyId(self._getStrategyId(sid))
        self._api2egQueue.put(apiEvent)
        
    def _onPositionData(self, apiEvent):
        '''成交通知'''
        dataAddr   = apiEvent.getData()
        fieldSize  = apiEvent.getFieldSize()
        fieldCount = apiEvent.getFieldCount()
        
        dataList = []
        
        for i in range(fieldCount):
            buf = string_at(dataAddr + fieldSize * i, fieldSize)
            data = EEquPositionNotice()
            memmove(addressof(data), buf, sizeof(EEquPositionNotice))
            
            idict = {
                'PositionNo'       : data.PositionNo.decode('utf-8'),
                'UserNo'           : data.UserNo.decode('utf-8'),
                'Sign'             : data.Sign.decode('utf-8'),
                'Cont'             : data.Cont.decode('utf-8'),
                'Direct'           : data.Direct.decode('utf-8'),
                'Hedge'            : data.Hedge.decode('utf-8'),
                'Deposit'          : data.Deposit,
                'PositionQty'      : data.PositionQty,
                'PrePositionQty'   : data.PrePositionQty,
                'PositionPrice'    : data.PositionPrice,
                'ProfitCalcPrice'  : data.ProfitCalcPrice,
                'FloatProfit'      : data.FloatProfit,
                'FloatProfitTBT'   : data.FloatProfitTBT,
            }
            dataList.append(idict)
        
        # 发送到引擎
        apiEvent.setData(dataList)
        sid = apiEvent.getSessionId()
        apiEvent.setStrategyId(self._getStrategyId(sid))
        self._api2egQueue.put(apiEvent)
        
        
    def _onMoney(self, apiEvent):
        '''资金查询应答'''
        dataAddr   = apiEvent.getData()
        fieldSize  = apiEvent.getFieldSize()
        fieldCount = apiEvent.getFieldCount()
        
        dataList = []
        
        for i in range(fieldCount):
            buf = string_at(dataAddr + fieldSize * i, fieldSize)
            data = EEquUserMoneyRsp()
            memmove(addressof(data), buf, sizeof(EEquUserMoneyRsp))
            
            idict = {
                'UserNo'        : data.UserNo.decode('utf-8'),
                'Sign'          : data.Sign.decode('utf-8'),
                'CurrencyNo'    : data.CurrencyNo.decode('utf-8'),
                'ExchangeRate'  : data.ExchangeRate,
                'FrozenFee'     : data.FrozenFee,
                'FrozenDeposit' : data.FrozenDeposit,
                'Fee'           : data.Fee,
                'Deposit'       : data.Deposit,
                'FloatProfit'   : data.FloatProfit,
                'FloatProfitTBT': data.FloatProfitTBT,
                'CoverProfit'   : data.CoverProfit,
                'CoverProfitTBT': data.CoverProfitTBT,
                'Balance'       : data.Balance,
                'Equity'        : data.Equity,
                'Available'     : data.Available,
                'UpdateTime'    : data.UpdateTime,
            }
            dataList.append(idict)
        
        # print(dataList)
        # 发送到引擎
        apiEvent.setData(dataList)
        self._api2egQueue.put(apiEvent)
