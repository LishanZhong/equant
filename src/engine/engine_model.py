from capi.event import *
from copy import deepcopy

class DataModel(object):
    def __init__(self, logger):
        self.logger = logger
        self._quoteModel = QuoteModel(logger)
        self._hisQuoteModel = HisQuoteModel(logger)
        self._tradeModel = TradeModel(logger)

    def getTradeModel(self):
        return self._tradeModel

    def getHisQuoteModel(self):
        return self._hisQuoteModel

    def getQuoteModel(self):
        return self._quoteModel
        
# 即时行情
class QuoteModel:
    def __init__(self, logger):
        self.logger = logger
        # 全量交易所、品种、合约
        self._exchangeData  = {}  #{key=ExchangeNo,value=ExchangeModel}
        self._commodityData = {}  #{key=CommodityNo, value=CommodityModel}
        self._contractData  = {}  #{key=ContractNo, value=QuoteDataModel}

        self._baseDataReady = False
        
    def getQuoteEvent(self, contractNo, strategyId):
        if contractNo not in self._contractData:
            return None
        contQuote = self._contractData[contractNo] 
        return contQuote.getEvent(strategyId)

    def getExchange(self):
        dataDict = {}
        for k, v in self._exchangeData.items():
            dataDict[k] = v.getExchange()
        return Event({'EventCode':EV_EG2ST_EXCHANGE_RSP, 'Data':dataDict})

    def getCommodity(self):
        dataDict = {}
        for k,v in self._commodityData.items():
            dataDict[k] = v.getCommodity()
        #TODO：先不拷贝
        return Event({'EventCode':EV_EG2ST_COMMODITY_RSP, 'Data':dataDict})

    # 交易所
    def updateExchange(self, apiEvent):
        dataList = apiEvent.getData()
        for dataDict in dataList:
            self._exchangeData[dataDict['ExchangeNo']] = ExchangeModel(self.logger, dataDict)
        if apiEvent.isChainEnd():
            self.logger.info('Initialize exchange data(%d) successfully!'%len(self._exchangeData))

    # 品种
    def updateCommodity(self, apiEvent):
        dataList = apiEvent.getData()
        for dataDict in dataList:
            self._commodityData[dataDict['CommodityNo']] = CommodityModel(self.logger, dataDict)    
        if apiEvent.isChainEnd():
            self.logger.info('Initialize commodity data(%d) successfully!' % len(self._commodityData))

    # 时间模板
    def updateTimeBucket(self, apiEvent):
        dataList = apiEvent.getData()

        if len(dataList) == 0:
            return 0

        dataDict = dataList[0]
        commodity = dataDict['Commodity']
        if commodity in self._commodityData:
            self._commodityData[commodity].updateTimeBucket(dataList)

        if apiEvent.isChainEnd():
            pass

    # 合约
    def updateContract(self, apiEvent):
        dataList = apiEvent.getData()
        for dataDict in dataList:
            self._contractData[dataDict['ContractNo']] = QuoteDataModel(self.logger, dataDict)
            
        if apiEvent.isChainEnd():
            self.logger.info('Initialize contract data(%d) successfully!'%len(self._contractData))
            self._baseDataReady = True

    def updateLv1(self, apiEvent):
        '''更新普通行情'''
        self._updateQuote(apiEvent, 'N')
       
    def updateLv2(self, apiEvent):
        '''更新深度行情'''
        self._updateQuote(apiEvent, 'D') 
        
    def _updateQuote(self, apiEvent, lv):
        contractNo = apiEvent.getContractNo()
        if contractNo not in self._contractData:
            #策略模块也使用该函数
            dataDict = {
                'ExchangeNo'  : '',
                'CommodityNo' : '',
                'ContractNo'  : contractNo,
            }
            self._contractData[contractNo] = QuoteDataModel(self.logger, dataDict)
            
        dataList = apiEvent.getData()
        data = self._contractData[contractNo]
        
        for oneDict in dataList:
            if lv == 'N':
                data.updateLv1(oneDict)
            else:
                data.updateLv2(oneDict)
        
class ExchangeModel:
    '''
    _metaData = {
        'ExchangeNo'   : 'ZCE',             #交易所编号
        'ExchangeName' : '郑州商品交易所'   #简体中文名称
    }
    '''
    def __init__(self, logger, dataDict):
        '''
        dataDict ={
            'ExchangeNo'  : value,
            'ExchangeName': value,
        } 
        '''
        self.logger = logger
        self._exchangeNo = dataDict['ExchangeNo']
        self._metaData = {
            'ExchangeNo'   : dataDict['ExchangeNo'],
            'ExchangeName' : dataDict['ExchangeName']
        }

    def getExchange(self):
        return self._metaData
        
class CommodityModel:
    '''
    _metaData = {
        'ExchangeNo'   : 'ZCE'             # value,str 交易所编号
        'CommodityNo'  : 'ZCE|F|SR'        # value,str 品种编号
        'CommodityType': 'F'               # value,str 品种类型
        'CommodityName': '白糖'            # value,str 品种名称
        'PriceNume'    : 1                 # value,float 报价分子
        'PriceDeno'    : 1                 # value,float 报价分母
        'PriceTick'    : 1                 # value,float 最小变动价
        'PricePrec'    : 1                 # value,float 价格精度
        'TradeDot'     : 10                # value,float 每手乘数
        'CoverMode'    : 'C'               # value,str 平仓方式，区分开平
        'TimeBucket'   : []                # 时间模板信息
    }
    '''
    def __init__(self, logger, dataDict):
        self.logger = logger
        self.commdityNo = dataDict['CommodityNo']
        timeBucket = dataDict['TimeBucket'] if 'TimeBucket' in dataDict else []

        self._metaData = {
            'ExchangeNo'    : dataDict['ExchangeNo'],
            'CommodityNo'   : dataDict['CommodityNo'],
            'CommodityType' : dataDict['CommodityType'],
            'CommodityName' : dataDict['CommodityName'],
            'PriceNume'     : dataDict['PriceNume'],
            'PriceDeno'     : dataDict['PriceDeno'],
            'PriceTick'     : dataDict['PriceTick'],
            'PricePrec'     : dataDict['PricePrec'],
            'TradeDot'      : dataDict['TradeDot'],
            'CoverMode'     : dataDict['CoverMode'],
            'TimeBucket'    : timeBucket,
        }
        
    def getCommodity(self):
        return self._metaData

    def updateTimeBucket(self, dataList):
        self._metaData['TimeBucket'] = dataList

class QuoteDataModel:
    '''
    _metaData = {
        'UpdateTime' : 20190401090130888, # 时间戳
        'Lv1Data'    : {                  # 普通行情
            '0'      : 5074,              # 昨收盘
            '1'      : 5052,              # 昨结算
            '2'      : 269272,            # 昨持仓
            '3'      : 5067,              # 开盘价
            '4'      : 5084,              # 最新价
            ...
            '126'    : 1                  # 套利行情系数
            },
        'Lv2BidData' :[
            5083,                         # 买1
            5082,                         # 买2
            5082,                         # 买3
            5080,                         # 买4
            5079,                         # 买5
        ],
        'Lv2AskData':[
            5084,                         # 卖1
            5085,                         # 卖2
            5086,                         # 卖3
            5087,                         # 卖4
            5088,                         # 卖5
        ]
    }
    '''
        
    def __init__(self, logger, dataDict):
        '''
        dataDict ={
            'ExchangeNo' : value,
            'CommodityNo': value,
            'ContractNo' : value,
        } 
        '''
        
        self.logger = logger
        self._contractNo = dataDict['ContractNo']
        self._metaData = {
            'ExchangeNo' : dataDict['ExchangeNo'],    # 交易所编号
            'CommodityNo': dataDict['CommodityNo'],   # 品种编号
            'UpdateTime' : 0,                         # 行情时间戳
            'Lv1Data'    : {},                        # 普通行情
            'Lv2BidData' : [0 for i in range(10)],    # 买深度
            'Lv2AskData' : [0 for i in range(10)]     # 卖深度
        }
        
    def getEvent(self, strategyId):
        data = deepcopy(self._metaData)
        msg = {
            'EventSrc'   : EEQU_EVSRC_ENGINE     ,  
            'EventCode'  : EV_EG2ST_SUBQUOTE_RSP ,
            'StrategyId' : strategyId            ,
            'SessionId'  : 0                     ,
            'ContractNo' : self._contractNo      ,
            'Data'       : data                  ,
        }

        return Event(msg)
        
    def updateLv1(self, oneDict):
        '''
        功能：更新普通行情
        参数: oneDict = {
            UpdateTime : value,
            FieldData  : {
                'FidMean1' : 'FidValue1',
                'FidMean2' : 'FidValue2'
                ...
            }
        }
        '''
        self._metaData['UpdateTime'] = oneDict['UpdateTime']
        fieldDict = oneDict['FieldData']
        
        for k, v in fieldDict.items():
            self._metaData['Lv1Data'][k] = v
        
    def updateLv2(self, oneDict):
        '''
        功能：更新深度行情
        参数：oneDict = {
            'Bid' : [
                {'Price' : Price1,  'Qty' : Qty1},
                {'Price' : Price2,  'Qty' : Qty2},
                ...
                {'Price' : Price10, 'Qty' : Qty10}
            ], 
            
            'Ask' : [
                {'Price' : Price1,  'Qty' : Qty1},
                {'Price' : Price2,  'Qty' : Qty2},
                ...
                {'Price' : Price10, 'Qty' : Qty10}
            ],
        }
        '''
        # 9.5传递全量深度，直接拷贝
        self._metaData['Lv2BidData'] = oneDict['Bid'][:]
        self._metaData['Lv2AskData'] = oneDict['Ask'][:]
        
            
# 历史行情
class HisQuoteModel:
    '''K线Model中不缓存，直接分发'''
    def __init__(self, logger):
        self.logger = logger
        
    def updateKline(self, apiEvent):
        strategyId = apiEvent.getStrategyId()
        sessionId = apiEvent.getSessionId()
        contractNo = apiEvent.getContractNo()
        klineType = apiEvent.getKLineType()
        data = apiEvent.getData()
        chain = apiEvent.getChain()
        #print("%d,%d,%s,%s,%s,%s"%(strategyId,sessionId, contractNo,klineType,chain, data))
        
# #####################################交易数据模型#########################################
class TLogoinModel:
    '''登录账号信息'''
    def __init__(self, logger, loginNo, data):
        self.logger = logger
        self._loginNo = loginNo
        
        # print("TLogoinModel", data)
        self._metaData = {
            'LoginNo'   : data['LoginNo']    ,  #登录账号
            'Sign'      : data['Sign']       ,  #标识
            'LoginName' : data['LoginName']  ,  #登录名称
            'LoginApi'  : data['LoginApi']   ,  #api类型
            'TradeDate' : data['TradeDate']  ,  #交易日期
            'IsReady'   : data['IsReady']       #是否准备就绪
        }
        self._userInfo = {}
        
        self.logger.info("[LOGIN]%s,%s,%s,%s,%s,%s"%(
            data['LoginNo'], data['Sign'], data['LoginName'],
            data['LoginApi'], data['TradeDate'], data['IsReady']
        ))
        
    def updateUserInfo(self, userNo, userInfo):
        self._userInfo[userNo] = userInfo

    def copyLoginInfoMetaData(self):
        return deepcopy(self._metaData) if len(self._metaData) > 0 else {}

class TUserInfoModel:
    '''资金账号信息'''
    def __init__(self, logger, login, data):
        self.logger = logger
        self._loginInfo = login
        self._userNo = data['UserNo']
        
        #print("TUserInfoModel", data)
        
        self._metaData = {
                'UserNo'    : data['UserNo'],
                'Sign'      : data['Sign'],
                'LoginNo'   : data['LoginNo'],
                'UserName'  : data['UserName'],
        }
        
        self._money   = {} #{'currencyNo' : TMoneyModel}
        self._order   = {} #{'OrderNo'    : TOrderModel}
        self._match   = {} #{'OrderNo'    : TMatchModel}
        self._position = {} #{'PositionNo' : TPostionModel}
        
        self.logger.info("[USER]%s,%s,%s,%s"%(
            data['UserNo'], data['Sign'], data['LoginNo'], data['UserName']
        ))

    def getMetaData(self):
        return self._metaData

    def updateMoney(self, data):
        currencyNo = data['CurrencyNo']
        if currencyNo not in self._money:
            self._money[currencyNo] = TMoneyModel(self.logger, data)
        else:
            self._money[currencyNo].updateMoney(data)

    def updateOrder(self, data):
        orderNo = data['OrderNo']
        if orderNo not in self._order:
            self._order[orderNo] = TOrderModel(self.logger, data)
        else:
            order = self._order[orderNo]
            order.updateOrder(data)

    def updateMatch(self, data):
        orderNo = data['OrderNo']
        if orderNo not in self._match:
            self._match[orderNo] = TMatchModel(self.logger, data)
        else:
            match = self._match[orderNo]
            match.updateMatch(data)

    def updatePosition(self, data):
        posNo = data['PositionNo']
        if posNo not in self._position:
            self._position[posNo] = TPositionModel(self.logger, data)
        else:
            pos = self._position[posNo]
            pos.updatePosition(data)

    def updateMoneyFromDict(self, moneyInfoDict):
        if len(moneyInfoDict) == 0:
            self._money = {}
            return

        for currencyNo, moneyDict in moneyInfoDict.items():
            if currencyNo not in self._money:
                self._money[currencyNo] = TMoneyModel(self.logger, moneyDict)
            else:
                self._money[currencyNo].updateMoney(moneyDict)

    def updateOrderFromDict(self, orderInfoDict):
        if len(orderInfoDict) == 0:
            self._order = {}
            return

        for orderNo, orderDict in orderInfoDict.items():
            if orderNo not in self._order:
                self._order[orderNo] = TOrderModel(self.logger, orderDict)
            else:
                self._order[orderNo].updateOrder(orderDict)

    def updateMatchFromDict(self, matchInfoDict):
        if len(matchInfoDict) == 0:
            self._match = {}
            return

        for orderNo, matchDict in matchInfoDict.items():
            if orderNo not in self._match:
                self._match[orderNo] = TMatchModel(self.logger, matchDict)
            else:
                self._match[orderNo].updateMatch(matchDict)

    def updatePositionFromDict(self, positionInfoDict):
        if len(positionInfoDict) == 0:
            self._position = {}
            return

        for positionNo, positionDict in positionInfoDict.items():
            if positionNo not in self._position:
                self._position[positionNo] = TPositionModel(self.logger, positionDict)
            else:
                self._position[positionNo].updatePosition(positionDict)

    def formatUserInfo(self):
        data = {
            'metaData' : {},
            'money'    : {},
            'order'    : {},
            'match'    : {},
            'position' : {},
        }

        if len(self._metaData) > 0:
            data['metaData'] = deepcopy(self._metaData)

        # 资金信息
        if len(self._money) > 0 :
            moneyDict = {}
            for currencyNo, tMoneyModel in self._money.items():
                moneyDict[currencyNo] = deepcopy(tMoneyModel._metaData)
            data['money'] = moneyDict

        # 订单信息
        if len(self._order) > 0:
            orderDict = {}
            for orderNo, tOrderModel in self._order.items():
                orderDict[orderNo] = deepcopy(tOrderModel._metaData)
            data['order'] = orderDict

        # 成交信息
        if len(self._match) > 0:
            matchDict = {}
            for orderNo, tMatchModel in self._match.items():
                matchDict[orderNo] = deepcopy(tMatchModel._metaData)
            data['match'] = matchDict

        # 委托信息
        if len(self._position) > 0:
            positionDict = {}
            for positionNo, tPositionModel in self._position.items():
                positionDict[positionNo] = deepcopy(tPositionModel._metaData)
            data['position'] = positionDict

        return data

class TMoneyModel:
    '''资金信息'''
    def __init__(self, logger, data):
        self.logger = logger
        self._metaData = {}
        self.updateMoney(data)
        
    def updateMoney(self, data):    
        self._metaData['UserNo']           = data['UserNo']        
        self._metaData['Sign']             = data['Sign']          
        self._metaData['CurrencyNo']       = data['CurrencyNo']       #币种号
        self._metaData['ExchangeRate']     = data['ExchangeRate']     #币种汇率
        self._metaData['FrozenFee']        = data['FrozenFee']        #冻结手续费
        self._metaData['FrozenDeposit']    = data['FrozenDeposit']    #冻结保证金
        self._metaData['Fee']              = data['Fee']              #手续费(包含交割手续费)
        self._metaData['Deposit']          = data['Deposit']          #保证金
        self._metaData['FloatProfit']      = data['FloatProfit']      #盯式盈亏，不含LME持仓盈亏
        self._metaData['FloatProfitTBT']   = data['FloatProfitTBT']   #逐笔浮赢
        self._metaData['CoverProfit']      = data['CoverProfit']      #盯市平盈
        self._metaData['CoverProfitTBT']   = data['CoverProfitTBT']   #逐笔平盈
        self._metaData['Balance']          = data['Balance']          #今资金=PreBalance+Adjust+CashIn-CashOut-Fee(TradeFee+DeliveryFee+ExchangeFee)+CoverProfitTBT+Premium
        self._metaData['Equity']           = data['Equity']           #今权益=Balance+FloatProfitTBT(NewFloatProfit+LmeFloatProfit)+UnExpiredProfit
        self._metaData['Available']        = data['Available']        #今可用=Equity-Deposit-Frozen(FrozenDeposit+FrozenFee)
        self._metaData['UpdateTime']       = data['UpdateTime']       #资金更新时间戳
        
        self.logger.info("[MONEY]%s,%f,%f,%f,%f,%f,%f,%f,%f,%f,%s"%(
            data['CurrencyNo'], data['Fee'],data['Deposit'], data['FloatProfit'],
            data['FloatProfitTBT'],data['CoverProfit'],data['CoverProfitTBT'],
            data['Balance'], data['Equity'],data['Available'],data['UpdateTime']
        ))
        
class TOrderModel:
    '''委托信息'''
    def __init__(self, logger, data):
        self.logger = logger
        self._metaData = {}
        self.updateOrder(data)
        
    def updateOrder(self, data):
        self._metaData['UserNo']            =  data['UserNo']          #             
        self._metaData['Sign']              =  data['Sign']           
        self._metaData['Cont']              =  data['Cont']              # 行情合约
        self._metaData['OrderType']         =  data['OrderType']         # 定单类型
        self._metaData['ValidType']         =  data['ValidType']         # 有效类型
        self._metaData['ValidTime']         =  data['ValidTime']         # 有效日期时间(GTD情况下使用)
        self._metaData['Direct']            =  data['Direct']            # 买卖方向
        self._metaData['Offset']            =  data['Offset']            # 开仓平仓 或 应价买入开平
        self._metaData['Hedge']             =  data['Hedge']             # 投机保值
        self._metaData['OrderPrice']        =  data['OrderPrice']        # 委托价格 或 期权应价买入价格
        self._metaData['TriggerPrice']      =  data['TriggerPrice']      # 触发价格
        self._metaData['TriggerMode']       =  data['TriggerMode']       # 触发模式
        self._metaData['TriggerCondition']  =  data['TriggerCondition']  # 触发条件
        self._metaData['OrderQty']          =  data['OrderQty']          # 委托数量 或 期权应价数量
        self._metaData['StrategyType']      =  data['StrategyType']      # 策略类型
        self._metaData['Remark']            =  data['Remark']            #下单备注字段，只有下单时生效。
        self._metaData['AddOneIsValid']     =  data['AddOneIsValid']     # T+1时段有效(仅港交所)
        self._metaData['OrderState']        =  data['OrderState']        # 委托状态
        self._metaData['OrderId']           =  data['OrderId']           # 定单号
        self._metaData['OrderNo']           =  data['OrderNo']           # 委托号
        self._metaData['MatchPrice']        =  data['MatchPrice']        # 成交价
        self._metaData['MatchQty']          =  data['MatchQty']          # 成交量
        self._metaData['ErrorCode']         =  data['ErrorCode']         # 最新信息码
        self._metaData['ErrorText']         =  data['ErrorText']         # 最新错误信息
        self._metaData['InsertTime']        =  data['InsertTime']        # 下单时间
        self._metaData['UpdateTime']        =  data['UpdateTime']        # 更新时间
        
        #self.logger.info("ORDER:%s,%f,%d"%(self._metaData['OrderNo'], self._metaData['OrderPrice'], self._metaData['OrderQty']))
        #print('updateOrder', self._metaData['OrderNo'], self._metaData['OrderPrice'], self._metaData['OrderQty'])
        
class TMatchModel:
    '''成交信息'''
    def __init__(self, logger, data):
        self.logger = logger
        self._metaData = {}
        self.updateMatch(data)
        
    def updateMatch(self, data):
        self._metaData['UserNo']            =  data['UserNo']          #             
        self._metaData['Sign']              =  data['Sign']           
        self._metaData['Cont']              =  data['Cont']              # 行情合约
        self._metaData['Direct']            =  data['Direct']            # 买卖方向
        self._metaData['Offset']            =  data['Offset']            # 开仓平仓 或 应价买入开平
        self._metaData['Hedge']             =  data['Hedge']             # 投机保值
        self._metaData['OrderNo']           =  data['OrderNo']           # 委托号
        self._metaData['MatchPrice']        =  data['MatchPrice']        # 成交价
        self._metaData['MatchQty']          =  data['MatchQty']          # 成交量
        self._metaData['FeeCurrency']       =  data['FeeCurrency']       # 手续费币种
        self._metaData['MatchFee']          =  data['MatchFee']          # 手续费
        self._metaData['MatchDateTime']     =  data['MatchDateTime']     # 成交时间
        self._metaData['AddOne']            =  data['AddOne']            # T+1成交
        self._metaData['Deleted']           =  data['Deleted']           # 是否删除
        
class TPositionModel:
    '''持仓信息'''
    def __init__(self, logger, data):
        self.logger = logger
        self._metaData = {}
        self.updatePosition(data)
        
    def updatePosition(self, data):
        self._metaData['PositionNo']        =  data['PositionNo']
        self._metaData['UserNo']            =  data['UserNo']            #             
        self._metaData['Sign']              =  data['Sign']           
        self._metaData['Cont']              =  data['Cont']              # 行情合约
        self._metaData['Direct']            =  data['Direct']            # 买卖方向
        self._metaData['Hedge']             =  data['Hedge']             # 投机保值
        self._metaData['Deposit']           =  data['Deposit']           # 初始保证金
        self._metaData['PositionQty']       =  data['PositionQty']        # 总持仓
        self._metaData['PrePositionQty']    =  data['PrePositionQty']          # 昨持仓数量
        self._metaData['PositionPrice']     =  data['PositionPrice']       # 价格
        self._metaData['ProfitCalcPrice']   =  data['ProfitCalcPrice']          # 浮盈计算价
        self._metaData['FloatProfit']       =  data['FloatProfit']     # 浮盈
        self._metaData['FloatProfitTBT']    =  data['FloatProfitTBT']            # 逐笔浮盈
        
class TradeModel:
    
    def __init__(self, logger):
        self.logger = logger
        
        self._loginInfo = {} #登录账号{'LoginNo': {:}}
        self._userInfo = {}  #资金账号{'UserNo' : {:}}
        
        #先简单写，不使用状态机
        self._dataStatus = TM_STATUS_NONE
        
    ###################################################################
    def getStatus(self):
        return self._dataStatus

    def getUserInfo(self):
        return self._userInfo

    def isUserFill(self):
        return self._dataStatus >= TM_STATUS_USER
        
    def isOrderFill(self):
        return self._dataStatus >= TM_STATUS_ORDER    
        
    def setStatus(self, status):
        self._dataStatus = status
    
    def getMoneyEvent(self):
        #查询所有账号下的资金信息
        eventList = []
        for v in self._userInfo.values():
            #外盘只查基币，内盘全查
            loginApi = v._loginInfo._metaData['LoginApi']
            currencyNo = ''
            if loginApi == 'DipperTradeApi':
                currencyNo = 'Base'
                
            event = Event({
                'StrategyId' : 0,
                'Data' : 
                    {
                        'UserNo'     : v._metaData['UserNo'],
                        'Sign'       : v._metaData['Sign'],
                        'CurrencyNo' : currencyNo
                    }
            })
            eventList.append(event)
            
        return eventList
        
    def getOrderEvent(self):
        #查询所有账号下的委托信息
        eventList = []
        for v in self._userInfo.values():
            event = Event({
                'StrategyId' : 0,
                'Data' : 
                    {
                        'UserNo'     : v._metaData['UserNo'],
                        'Sign'       : v._metaData['Sign'],
                    }
            })
            eventList.append(event)
            
        return eventList
        
    def getMatchEvent(self):
        return self.getOrderEvent()
        
    def getPositionEvent(self):
        return self.getOrderEvent()

    def getTradeInfoEvent(self, stragetyId):
        pass


    ###################################################################
    def TLogoinModel(self, apiEvent):
        dataList = apiEvent.getData()

        for data in dataList:
            self._loginInfo[data['LoginNo']] = TLogoinModel(self.logger, data['LoginNo'], data)

    # 更新登录信息
    def updateLoginInfo(self, apiEvent):
        dataList = apiEvent.getData()
        for data in dataList:
            loginNo = data['LoginNo']
            if loginNo not in self._loginInfo:
                self._loginInfo[loginNo] = TLogoinModel(self.logger, loginNo, data)

    def updateLoginInfoFromDict(self, loginInfoDict):
        if len(loginInfoDict) == 0:
            return

        for loginNo, loginInfo in loginInfoDict.items():
            self._loginInfo[loginNo] = TLogoinModel(self.logger, loginNo, loginInfo)

    def updateUserInfoFromDict(self, userInfoDict):
        if len(userInfoDict) == 0:
            return

        for userNo, userInfo in userInfoDict.items():
            # 资金账号信息
            metaData = userInfo['metaData']
            tUserInfoModel = TUserInfoModel(self.logger, self._loginInfo, metaData)

            # 更新资金信息
            moneyInfoDict = userInfo['money']
            tUserInfoModel.updateMoneyFromDict(moneyInfoDict)

            # 更新订单信息
            orderInfoDict = userInfo['order']
            tUserInfoModel.updateOrderFromDict(orderInfoDict)

            # 更新成交信息
            matchInfoDict = userInfo['match']
            tUserInfoModel.updateMatchFromDict(matchInfoDict)

            # 更新持仓信息
            positionInfoDict = userInfo['position']
            tUserInfoModel.updatePositionFromDict(positionInfoDict)

            self._userInfo[userNo] = tUserInfoModel


    def updateUserInfo(self, apiEvent):
        dataList = apiEvent.getData()
        for data in dataList:
            loginNo = data['LoginNo']
            if loginNo not in self._loginInfo:
                self.logger.error("The login account(%s) doesn't login!"%loginNo)
                continue
                
            loginInfo = self._loginInfo[loginNo]
            userNo = data['UserNo']
            userInfo = TUserInfoModel(self.logger, loginInfo, data)

            self._loginInfo[loginNo].updateUserInfo(userNo, userInfo)
            self._userInfo[userNo] = userInfo
        
        #print(apiEvent.getData())

    def updateMoney(self, apiEvent):
        dataList = apiEvent.getData()

        for data in dataList:
            userNo = data['UserNo']
            if userNo not in self._userInfo:
                self.logger.error("[updateMoney]The user account(%s) doesn't login!"%userNo)
                continue
            self._userInfo[userNo].updateMoney(data)
            
        #print(apiEvent.getData())
        
    def updateOrderData(self, apiEvent):
        dataList = apiEvent.getData()

        for data in dataList:
            userNo = data['UserNo']
            if userNo not in self._userInfo:
                self.logger.error("[updateOrderData]The user account(%s) doesn't login!"%userNo)
                continue
                
            self.logger.debug('[ORDER]%s'%data)
        
            self._userInfo[userNo].updateOrder(data)
            
    def updateMatchData(self, apiEvent):
        dataList = apiEvent.getData()
        
        for data in dataList:
            userNo = data['UserNo']
            if userNo not in self._userInfo:
                self.logger.error("[updateMatchData]The user account(%s) doesn't login!"%userNo)
                continue
            
            self.logger.debug('[MATCH]%s'%data)
        
            self._userInfo[userNo].updateMatch(data)
            
    def updatePosData(self, apiEvent):
        dataList = apiEvent.getData()
        
        for data in dataList:
            userNo = data['UserNo']
            if userNo not in self._userInfo:
                self.logger.error("[updatePosData]The user account(%s) doesn't login!"%userNo)
                continue
                
            self.logger.debug('[POS]%s'%data)
        
            self._userInfo[userNo].updatePosition(data)