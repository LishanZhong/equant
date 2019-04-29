#-*-:conding:utf-8-*-

from multiprocessing import Process, Queue
from threading import Thread
from .strategy import StartegyManager
from capi.py2c import PyAPI
from capi.event import *
import time, queue
from .engine_model import DataModel
import copy


class StrategyEngine(object):
    '''策略引擎'''
    def __init__(self, logger, eg2uiQueue, ui2egQueue):
        self.logger = logger
        
        # Engine->Ui, 包括资金，权益等
        self._eg2uiQueue = eg2uiQueue
        # Ui->Engine, 包括策略加载等
        self._ui2egQueue = ui2egQueue
        
    def _initialize(self):
        '''进程中初始化函数'''
        self.logger.info('Initialize strategy engine!')
        
        # 数据模型
        self._dataModel = DataModel(self.logger)
        self._qteModel = self._dataModel.getQuoteModel()
        self._hisModel = self._dataModel.getHisQuoteModel()
        self._trdModel = self._dataModel.getTradeModel()
        
        # api回调函数
        self._regApiCallback()
        # 策略发送函数
        self._regMainWorkFunc()
        
        # Api->Engine, 品种、行情、K线、交易等
        self._api2egQueue = queue.Queue()
        # Strategy->Engine, 初始化、行情、K线、交易等
        self._st2egQueue = Queue()
        # 创建主处理线程, 从api和策略进程收数据处理
        self._startMainThread()
        # 创建_pyApi对象
        self._pyApi = PyAPI(self.logger, self._api2egQueue) 
        
        # 策略编号，自增
        self._maxStrategyId = 1
        # 创建策略管理器
        self._strategyMgr = StartegyManager(self.logger, self._st2egQueue)
        
        # 策略进程队列列表
        self._eg2stQueueDict = {} #{strategy_id, queue}
        
        # 即时行情订阅列表
        self._contStrategyDict = {} #{'contractNo' : [strategyId1, strategyId2...]}
        # 历史K线订阅列表
        self._hisContStrategyDict = {} #{'contractNo' : [strategyId1, strategyId2...]}
        
        self.logger.debug('Initialize strategy engine ok!')
        
    def _regApiCallback(self):
        self._apiCallbackDict = {
            EEQU_SRVEVENT_CONNECT           : self._onApiConnect               ,
            EEQU_SRVEVENT_DISCONNECT        : self._onApiDisconnect            ,
            EEQU_SRVEVENT_EXCHANGE          : self._onApiExchange              ,
            EEQU_SRVEVENT_COMMODITY         : self._onApiCommodity             ,
            EEQU_SRVEVENT_CONTRACT          : self._onApiContract              ,
            EEQU_SRVEVENT_TIMEBUCKET        : self._onApiTimeBucket            ,
            EEQU_SRVEVENT_QUOTESNAP         : self._onApiSnapshot              ,
            EEQU_SRVEVENT_QUOTESNAPLV2      : self._onApiDepthQuote            ,
            EEQU_SRVEVENT_HISQUOTEDATA      : self._onApiKlinedataRsp          ,
            EEQU_SRVEVENT_HISQUOTENOTICE    : self._onApiKlinedataNotice       ,
            EEQU_SRVEVENT_TRADE_LOGINQRY    : self._onApiLoginInfo             ,
            EEQU_SRVEVENT_TRADE_USERQRY     : self._onApiUserInfo              ,
            EEQU_SRVEVENT_TRADE_LOGINNOTICE : self._onApiLoginInfo             ,
            EEQU_SRVEVENT_TRADE_ORDERQRY    : self._onApiOrderDataQry          ,
            EEQU_SRVEVENT_TRADE_ORDER       : self._onApiOrderData             ,
            EEQU_SRVEVENT_TRADE_MATCHQRY    : self._onApiMatchDataQry           ,
            EEQU_SRVEVENT_TRADE_MATCH       : self._onApiMatchData             ,
            EEQU_SRVEVENT_TRADE_POSITQRY    : self._onApiPosDataQry            ,
            EEQU_SRVEVENT_TRADE_POSITION    : self._onApiPosData               ,
            EEQU_SRVEVENT_TRADE_FUNDQRY     : self._onApiMoney                 ,
            EV_EG2ST_ACTUAL_ORDER_SESSION_MAP : self._onOrderSessionMap,
        }
        
    def _regMainWorkFunc(self):
        self._mainWorkFuncDict = {
            EV_ST2EG_EXCHANGE_REQ           : self._onExchange                 ,
            EV_ST2EG_COMMODITY_REQ          : self._reqCommodity               ,
            EV_ST2EG_SUB_QUOTE              : self._reqSubQuote                ,
            EV_ST2EG_UNSUB_QUOTE            : self._reqUnsubQuote              ,
            EV_ST2EG_SUB_HISQUOTE           : self._reqSubHisquote             ,
            EV_ST2EG_UNSUB_HISQUOTE         : self._reqUnsubHisquote           ,
            EV_ST2EG_SWITCH_STRATEGY        : self._reqKLineStrategySwitch     ,
            #
            EV_ST2EG_NOTICE_KLINEDATA       : self._sendKLineData,
            EV_ST2EG_UPDATE_KLINEDATA       : self._sendKLineData,

            # k line series
            EV_ST2EG_ADD_KLINESERIES        : self._addSeries,
            EV_ST2EG_NOTICE_KLINESERIES     : self._sendKLineSeries,
            EV_ST2EG_UPDATE_KLINESERIES     : self._sendKLineSeries,

            # k line signal
            EV_ST2EG_ADD_KLINESIGNAL        : self._addSignal,
            EV_ST2EG_NOTICE_KLINESIGNAL     : self._sendKLineSignal,
            EV_ST2EG_UPDATE_KLINESIGNAL     : self._sendKLineSignal,

            # 暂停、恢复、与退出
            EV_UI2EG_STRATEGY_PAUSE         : self._onStrategyPause,
            EV_UI2EG_STRATEGY_RESUME        : self._onStrategyResume,
            EV_UI2EG_EQUANT_EXIT            : self._onEquantExit,

            EV_ST2EG_UPDATE_STRATEGYDATA    : self._reqStrategyDataUpdateNotice,
            EV_EG2UI_REPORT_RESPONSE        : self._reportResponse,
            EV_EG2UI_CHECK_RESULT           : self._checkResponse,
            EV_EG2ST_MONITOR_INFO           : self._monitorResponse,

            # load strategy
            EV_EG2UI_LOADSTRATEGY_RESPONSE  : self._loadStrategyResponse,
            EV_EG2UI_STRATEGY_STATUS        : self._starategyStatus,

            EV_ST2EG_STRATEGYTRADEINFO      : self._reqTradeInfo,
            EV_ST2EG_ACTUAL_ORDER           : self._sendOrder,
            EV_ST2EG_ACTUAL_CANCEL_ORDER    : self._deleteOrder,
            EV_ST2EG_ACTUAL_MODIFY_ORDER    : self._modifyOrder,
        }
            
    def run(self):
        # 在当前进程中初始化
        self._initialize()
        
        while True:
            self._handleUIData()
            
    def _sendEvent2Strategy(self, strategyId, event):
        if strategyId not in self._eg2stQueueDict:
            return
        eg2stQueue = self._eg2stQueueDict[strategyId]
        eg2stQueue.put(event)
        
    def _sendEvent2AllStrategy(self, event):
        for id in self._eg2stQueueDict:
            self._eg2stQueueDict[id].put(event)
        
    def _dispathQuote2Strategy(self, code, apiEvent):
        '''分发即时行情'''
        apiData = apiEvent.getData()
        contractNo = apiEvent.getContractNo()
        contStList = self._contStrategyDict[contractNo]
        
        data = apiData[:]
        
        msg = {
            'EventSrc'     :  EEQU_EVSRC_ENGINE,
            'EventCode'    :  code,
            'StrategyId'   :  0,
            'SessionId'    :  0,
            'UserNo'       :  '',
            'ContractNo'   :  contractNo,
            'Data'         :  data
        }
        
        event = Event(msg)
        
        for id in contStList:
            self._sendEvent2Strategy(id, event)
            
    # //////////////////////UI事件处理函数/////////////////////
    def _handleUIData(self):
        try:
            event = self._ui2egQueue.get()
            if type(event) is dict:
                event = Event(event)
            code  = event.getEventCode()
            if code == EV_UI2EG_LOADSTRATEGY:
                # 加载策略事件
                self._loadStrategy(event)
            elif code == EV_UI2EG_REPORT:
                self._noticeStrategyReport(event)
        except queue.Empty as e:
            pass

    #
    def _noticeStrategyReport(self, event):
        self._strategyMgr.sendEvent2Strategy(event.getStrategyId(), event)

    def _getStrategyId(self):
        id = self._maxStrategyId
        self._maxStrategyId += 1
        return id

    def _loadStrategy(self, event):
        id = self._getStrategyId()
        eg2stQueue = Queue(2000)
        self._eg2stQueueDict[id] = eg2stQueue
        self._strategyMgr.create(id, eg2stQueue, event)

        # =================
        self._strategyMgr.sendEvent2Strategy(id, event)

    def _loadStrategyResponse(self, event):
        self._eg2uiQueue.put(event)
        
    def _starategyStatus(self, event):
        self._eg2uiQueue.put(event)
        
    #////////////////api回调及策略请求事件处理//////////////////
    def _handleApiData(self):
        try:
            apiEvent = self._api2egQueue.get_nowait()
            code  = apiEvent.getEventCode()
            # print("c api code =", code)
            if code not in self._apiCallbackDict:
                return
            self._apiCallbackDict[code](apiEvent)
        except queue.Empty as e:
            pass
            
    def _handelStData(self):
        try:
            event = self._st2egQueue.get_nowait()
            code  = event.getEventCode()
            if code not in self._mainWorkFuncDict:
                self.logger.debug('Event %d not register in _mainWorkFuncDict'%code)
                #print("未处理的event code =",code)
                return
            self._mainWorkFuncDict[code](event)
        except (queue.Empty, KeyError) as e:
            if e is KeyError:
                event.printTool()
                print(" now code is ", code)
            pass
            
    def _mainThreadFunc(self):
        while True:
            self._handleApiData()
            self._handelStData()
            #time.sleep(0.01)
            
    def _startMainThread(self):
        '''从api队列及策略队列中接收数据'''
        self._apiThreadH = Thread(target=self._mainThreadFunc)
        self._apiThreadH.start()
        
    def _moneyThreadFunc(self):
        while True:
            eventList = self._trdModel.getMoneyEvent()
            #查询所有账户下的资金
            for event in eventList:
                self._reqMoney(event)
                
            time.sleep(60)
                
    def _createMoneyTimer(self):
        '''资金查询线程'''
        self._moneyThreadH = Thread(target=self._moneyThreadFunc)
        self._moneyThreadH.start()
        
    #////////////////api回调事件//////////////////////////////
    def _onApiConnect(self, apiEvent):
        self._pyApi.reqExchange(Event({'StrategyId':0, 'Data':''}))
        
    def _onApiDisconnect(self, apiEvent):
        '''
        断连事件：区分与9.5/交易/即时行情/历史行情
            1. 与9.5断连：
                a. 停止所有策略(包括回测与运行)
                b. 通知界面断连状态
                c. 设置引擎状态为与9.5断连
                d. 清理所有数据，重置数据状态
            2. 与即时行情断连
                a. 停止所有策略(运行)
                b  通知界面断连状态
                c. 设置引擎状态为与即时行情断连
                d. 清理所有即时行情数据
                
            3. 与历史行情断连
                a. 停止所有策略（包括回测和运行）
                b. 通知界面断连状态
                c. 设置引擎状态为与历史行情断连
                d. 清理所有历史K线数据
                
            4. 与交易断连
                a. 停止所有策略(运行)
                b. 通知界面断连状态
                c. 设置引擎状态为与交易断开链接
                d. 清理所有交易数据
                
            说明：策略停止后，所有相关数据清理
                
        '''
        #
        
    
    def _onApiExchange(self, apiEvent):  
        self._qteModel.updateExchange(apiEvent)

        self._sendEvent2Strategy(apiEvent.getStrategyId(), apiEvent)

        self._eg2uiQueue.put(apiEvent)
        if apiEvent.isChainEnd():
            self._pyApi.reqCommodity(Event({'StrategyId':0, 'Data':''}))
        
    def _onApiCommodity(self, apiEvent):
        self._qteModel.updateCommodity(apiEvent)
        self._eg2uiQueue.put(apiEvent)

        if apiEvent.isChainEnd():
            self._pyApi.reqContract(Event({'StrategyId':0, 'Data':''}))

        # 发送商品交易时间模板请求
        dataList = apiEvent.getData()
        for dataDict in dataList:
            event = Event({
                'EventCode': EV_ST2EG_TIMEBUCKET_REQ,
                'StrategyId': apiEvent.getStrategyId(),
                'Data': dataDict['CommodityNo'],
            })
            self._pyApi.reqTimebucket(event)
        
    def _onApiContract(self, apiEvent):  
        self._qteModel.updateContract(apiEvent)
        self._eg2uiQueue.put(apiEvent)
        if apiEvent.isChainEnd():
            self._pyApi.reqQryLoginInfo(Event({'StrategyId':0, 'Data':''}))
        
    def _onApiTimeBucket(self, apiEvent):
        self._qteModel.updateTimeBucket(apiEvent)
        
    def _onApiSnapshot(self, apiEvent):
        self._qteModel.updateLv1(apiEvent)
        self._dispathQuote2Strategy(EV_EG2ST_SNAPSHOT_NOTICE, apiEvent)
        
    def _onApiDepthQuote(self, apiEvent):
        self._qteModel.updateLv2(apiEvent)
        self._dispathQuote2Strategy(EV_EG2ST_DEPTH_NOTICE, apiEvent)
        
    def _onApiKlinedataRsp(self, apiEvent):
        self._onApiKlinedata(apiEvent, EV_EG2ST_HISQUOTE_RSP)
        
    def _onApiKlinedataNotice(self, apiEvent):
        self._onApiKlinedata(apiEvent, EV_EG2ST_HISQUOTE_NOTICE)
        
    def _onApiKlinedata(self, apiEvent, code):
        self._hisModel.updateKline(apiEvent)
        strategyId = apiEvent.getStrategyId()
        #策略号为0，认为是推送数据
        apiData = apiEvent.getData()
        data = apiData[:]
        event = Event({
            'StrategyId' : strategyId,
            'EventCode'  : code,
            'ChainEnd'   : apiEvent.getChain(),
            'ContractNo' : apiEvent.getContractNo(),
            'KLineType'  : apiEvent.getKLineType(),
            'KLineSlice' : apiEvent.getKLineSlice(),
            'Data'       : data
        })
        
        if strategyId > 0:
            self._sendEvent2Strategy(strategyId, event)
            return
            
        #推送数据，分发
        contNo = apiEvent.getContractNo()
        if contNo not in self._hisContStrategyDict:
            return

        stDict = self._hisContStrategyDict[contNo]
        for key in stDict:
            event.setStrategyId(key)
            self._sendEvent2Strategy(key, event)

    # 用户登录信息
    def _onApiLoginInfo(self, apiEvent):
        self._trdModel.updateLoginInfo(apiEvent)
        self._sendEvent2AllStrategy(apiEvent)

        if not apiEvent.isChainEnd():
            return       
        if not apiEvent.isSucceed():
            return

        self._trdModel.setStatus(TM_STATUS_LOGIN)
        self._reqUserInfo(Event({'StrategyId':0, 'Data':''}))

    # 账户信息
    def _onApiUserInfo(self, apiEvent):
        self._trdModel.updateUserInfo(apiEvent)
        self._eg2uiQueue.put(apiEvent)
        # print("++++++ 账户信息 引擎 ++++++", apiEvent.getData())
        self._sendEvent2AllStrategy(apiEvent)

        if not apiEvent.isChainEnd():
            return       
        if not apiEvent.isSucceed():
            return
        
        self._trdModel.setStatus(TM_STATUS_USER)
        # 查询所有账户下委托信息
        eventList = self._trdModel.getOrderEvent()

        for event in eventList:
            # print("====== 查询所有账户下委托信息 ======", event.getData())
            self._reqOrder(event)
        
    def _onApiOrderDataQry(self, apiEvent):
        self._trdModel.updateOrderData(apiEvent)
        # print("++++++ 订单信息 引擎 查询 ++++++", apiEvent.getData())
        # TODO: 分块传递
        self._sendEvent2AllStrategy(apiEvent)

        if not apiEvent.isChainEnd():
            return
        if not apiEvent.isSucceed():
            return
            
        self._trdModel.setStatus(TM_STATUS_ORDER)
        #查询所有账户下成交信息
        eventList = self._trdModel.getMatchEvent()
        for event in eventList:
            self._reqMatch(event)
        
    def _onApiOrderData(self, apiEvent):
        # 订单信息
        self._trdModel.updateOrderData(apiEvent)
        # print("++++++ 订单信息 引擎 变化 ++++++", apiEvent.getData())
        # TODO: 分块传递
        self._sendEvent2AllStrategy(apiEvent)
        
    def _onApiMatchDataQry(self, apiEvent):
        self._trdModel.updateMatchData(apiEvent)
        # print("++++++ 成交信息 引擎 查询 ++++++", apiEvent.getData())
        # TODO: 分块传递
        self._sendEvent2AllStrategy(apiEvent)

        if not apiEvent.isChainEnd():
            return
        if not apiEvent.isSucceed():
            return
            
        self._trdModel.setStatus(TM_STATUS_MATCH)
        #查询所有账户下成交信息
        eventList = self._trdModel.getPositionEvent()
        for event in eventList:
            self._reqPosition(event)
            
    def _onApiMatchData(self, apiEvent):
        # 成交信息
        self._trdModel.updateMatchData(apiEvent)
        # print("++++++ 成交信息 引擎 变化 ++++++", apiEvent.getData())
        # TODO: 分块传递
        self._sendEvent2AllStrategy(apiEvent)
        
    def _onApiPosDataQry(self, apiEvent):
        self._trdModel.updatePosData(apiEvent)
        # print("++++++ 持仓信息 引擎 查询 ++++++", apiEvent.getData())
        # TODO: 分块传递
        self._sendEvent2AllStrategy(apiEvent)

        if not apiEvent.isChainEnd():
            return
        if not apiEvent.isSucceed():
            return
            
        self._trdModel.setStatus(TM_STATUS_POSITION)
        
        #交易基础数据查询完成，定时查询资金
        self._createMoneyTimer()
            
    def _onApiPosData(self, apiEvent):
        # 持仓信息
        self._trdModel.updatePosData(apiEvent)
        # print("++++++ 持仓信息 引擎 变化 ++++++", apiEvent.getData())
        # TODO: 分块传递
        self._sendEvent2AllStrategy(apiEvent)

    def _onApiMoney(self, apiEvent):
        # 资金信息
        self._trdModel.updateMoney(apiEvent)
        # print("++++++ 资金信息 引擎 ++++++", apiEvent.getData())
        self._sendEvent2AllStrategy(apiEvent)

    def _onOrderSessionMap(self, event):
        self._sendEvent2Strategy(event.getStrategyId(), event)

    def _reqTradeInfo(self, event):
        '''
        查询账户信息，如果用户未登录，则Data返回为空
        '''
        stragetyId = event.getStrategyId()
        if len(self._trdModel._loginInfo) == 0:
            trdEvent = Event({
                'EventCode': EV_EG2ST_TRADEINFO_RSP,
                'StrategyId': stragetyId,
                'Data': '',
            })
            self._sendEvent2Strategy(stragetyId, trdEvent)
            return 0

        data = {
            'loginInfo' : {}, # 登录账号信息
            'userInfo'  : {}, # 资金账号信息
        }
        # 登录账号信息
        loginInfoDict = {}
        for userNo, tLoginModel in self._trdModel._loginInfo.items():
            loginInfoDict[userNo] = tLoginModel.copyLoginInfoMetaData()
        data['loginInfo'] = loginInfoDict

        # 资金账号信息
        userInfoDict = {}
        for userNo, tUserInfoModel in self._trdModel._userInfo.items():
            userInfoDict[userNo] = tUserInfoModel.formatUserInfo()
        data['userInfo'] = userInfoDict

        stragetyId = event.getStrategyId()
        trdEvent = Event({
            'EventCode': EV_EG2ST_TRADEINFO_RSP,
            'StrategyId': stragetyId,
            'Data': data,
        })
        self._sendEvent2Strategy(stragetyId, trdEvent)

    #///////////////策略进程事件////////////////////////////// 
    def _addSubscribe(self, contractNo, strategyId):
        stDict = self._contStrategyDict[contractNo]
        # 重复订阅
        if strategyId in stDict:
            return
        stDict[strategyId] = None
            
    def _sendQuote(self, contractNo, strategyId):
        event = self._qteModel.getQuoteEvent(contractNo, strategyId)
        self._sendEvent2Strategy(strategyId, event)

    def _onExchange(self, event):
        '''查询交易所信息'''
        revent = self._qteModel.getExchange()
        self._sendEvent2Strategy(event.getStrategyId(), revent)

    def _reqCommodity(self, event):
        '''查询品种信息'''
        revent = self._qteModel.getCommodity()
        self._sendEvent2Strategy(event.getStrategyId(), revent)
    
    def _reqSubQuote(self, event):
        '''订阅即时行情'''
        contractList = event.getData()
        strategyId = event.getStrategyId()
        
        subList = []
        for contractNo in contractList:
            if contractNo not in self._contStrategyDict:
                subList.append(contractNo)
                self._contStrategyDict[contractNo] = {strategyId:None}
            else:
                if strategyId in self._contStrategyDict[contractNo]:
                    continue #重复订阅，不做任何处理
                self._contStrategyDict[contractNo][strategyId] = None
                self._sendQuote(contractNo, strategyId)
        
        if len(subList) > 0:
            event.setData(subList)
            self._pyApi.reqSubQuote(event)
    
    def _reqUnsubQuote(self, event):
        '''退订即时行情'''
        strategyId = event.getStrategyId()
        contractList = event.getData()
        
        unSubList = []
        for contNo in contractList:
            if contNo not in self._contStrategyDict:
                continue #该合约没有订阅
            stDict = self._contStrategyDict[contNo]
            if strategyId not in stDict:
                continue #该策略没有订阅
            stDict.pop(strategyId)
            #已经没有人订阅了，退订吧
            if len(stDict) <= 0:
                unSubList.append(contNo)
                
        if len(unSubList) > 0:
            event.setData(unSubList)
            self._pyApi.reqUnsubQuote(event)
        
    # def _reqTimebucket(self, event):
    #     '''查询时间模板'''
    #     self._pyApi.reqTimebucket(event)
        
    def _reqSubHisquote(self, event): 
        '''订阅历史行情'''
        data = event.getData()
        if data['NeedNotice'] == EEQU_NOTICE_NOTNEED:
            self._pyApi.reqSubHisquote(event)
            return
        
        strategyId = event.getStrategyId()
        data = event.getData()
        contNo = data['ContractNo']

        if contNo not in self._hisContStrategyDict:
            self._hisContStrategyDict[contNo] = {strategyId:None}
        
        stDict = self._hisContStrategyDict[contNo]  
        if strategyId not in stDict:
            stDict[strategyId] = None
            
        self._pyApi.reqSubHisquote(event)
        
    def _reqUnsubHisquote(self, event):
        '''退订历史行情'''
        strategyId = event.getStrategyId()
        data = event.getData()
        contNo = data['ContractNo']
        
        if contNo not in self._hisContStrategyDict:
            return #该合约没有订阅
        stDict = self._hisContStrategyDict[contNo]

        if strategyId not in stDict:
            return #该策略没有订阅
        stDict.pop(strategyId)
        #已经没有人订阅了，退订吧
        unSubList = []
        if len(stDict) <= 0:
            unSubList.append(contNo)
        if len(unSubList) > 0:
            self._pyApi.reqUnsubHisquote(event)
        
    def _reqKLineStrategySwitch(self, event):
        '''切换策略图'''
        self._pyApi.reqKLineStrategySwitch(event)
        
    def _reqKLineDataResult(self, event):
        '''推送回测K线数据'''
        self._pyApi.reqKLineDataResult(event)
        
    def _reqKLineDataResultNotice(self, event):
        '''更新实盘K线数据'''
        self._pyApi.reqKLineDataResultNotice(event)
        
    def _reqAddKLineSeriesInfo(self, event):
        '''增加指标数据'''
        self._pyApi.addSeries(event)
        
    def _reqKLineSeriesResult(self, event):
        '''推送回测指标数据'''
        self._pyApi.sendSeries(event)
        
    def _reqAddKLineSignalInfo(self, event):
        '''增加信号数据'''
        self._pyApi.addSignal(event)
        
    def _reqKLineSignalResult(self, event):
        '''推送回测信号数据'''
        self._pyApi.sendSignal(event)
        
    def _reqStrategyDataUpdateNotice(self, event):
        '''刷新指标、信号通知'''
        self._pyApi.reqStrategyDataUpdateNotice(event)

    def _reportResponse(self, event):
        #print(" engine 进程，收到策略进程的report 结果，并向ui传递")
        self._eg2uiQueue.put(event)

    def _checkResponse(self, event):
        #print(" engine 进程，收到策略进程的检查结果，并向ui传递")
        self._eg2uiQueue.put(event)

    def _monitorResponse(self, event):
        self._eg2uiQueue.put(event)
    ################################交易请求#########################
    def _reqUserInfo(self, event):
        self._pyApi.reqQryUserInfo(event)
        
    def _reqOrder(self, event):
        self._pyApi.reqQryOrder(event)
        
    def _reqMatch(self, event):
        self._pyApi.reqQryMatch(event)
        
    def _reqPosition(self, event):
        self._pyApi.reqQryPosition(event)
         
    def _reqMoney(self, event):
        self._pyApi.reqQryMoney(event)

    def _sendOrder(self, event):
        # 委托下单，发送委托单
        self._pyApi.reqInsertOrder(event)

    def _deleteOrder(self, event):
        # 委托撤单
        self._pyApi.reqCancelOrder(event)

    def _modifyOrder(self, event):
        # 委托改单
        self._pyApi.reqModifyOrder(event)

    def _sendKLineData(self, event):
        '''推送K线数据'''
        if event.getEventCode() == EV_ST2EG_NOTICE_KLINEDATA:
            self._pyApi.sendKLineData(event, 'N')
        elif event.getEventCode() == EV_ST2EG_UPDATE_KLINEDATA:
            self._pyApi.sendKLineData(event, 'U')

    def _addSeries(self, event):
        '''增加指标线'''
        self._pyApi.addSeries(event)

    def _sendKLineSeries(self, event):
        '''推送指标数据'''
        if event.getEventCode() == EV_ST2EG_NOTICE_KLINESERIES:
            self._pyApi.sendKLineSeries(event, 'N')
        elif event.getEventCode() == EV_ST2EG_UPDATE_KLINESERIES:
            self._pyApi.sendKLineSeries(event, 'U')

    def _addSignal(self, event):
        '''增加信号线'''
        self._pyApi.addSignal(event)

    def _sendKLineSignal(self, event):
        '''推送信号数据'''
        if event.getEventCode() == EV_ST2EG_NOTICE_KLINESIGNAL:
            self._pyApi.sendKLineSignal(event, 'N')
        elif event.getEventCode() == EV_ST2EG_UPDATE_KLINESIGNAL:
            self._pyApi.sendKLineSignal(event, 'U')

    # 暂停当前策略
    def _onStrategyPause(self, event):
        self._sendEvent2Strategy(event.getStrategyId(), event)

    # 恢复当前策略
    def _onStrategyResume(self, event):
        self._sendEvent2Strategy(event.getStrategyId(), event)

    #  当量化退出时，发事件给所有的策略
    def _onEquantExit(self, event):
        # self._sendEvent2AllStrategy(event)
        import json
        # 保存到文件
        context = self._strategy.getEnvironment()
        jsonFile = open('StrategyContext.json', 'w', encoding='utf-8')
        json.dump(context, jsonFile, ensure_ascii=False, indent=4)