import numpy as np
from capi.com_types import *
from .engine_model import *
from copy import deepcopy
import talib
import time
from report.calc import CalcCenter
import copy

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class StrategyModel(object):
    def __init__(self, strategy):
        self._strategy = strategy
        self.logger = strategy.logger
        self._argsDict = strategy._argsDict
       
        self._plotedDict = {}
        
        #Notice：会抛异常
        self._cfgModel = StrategyConfig(self._argsDict)
        #回测计算
        self._calcCenter = self._createCalc()
        
        self._qteModel = StrategyQuote(strategy, self._cfgModel)
        self._hisModel = StrategyHisQuote(strategy, self._cfgModel, self._calcCenter)
        self._trdModel = StrategyTrade(strategy, self._cfgModel)

        #
        self._runBarInfo = BarInfo(self.logger)

    def setRunStatus(self, status):
        self._runStatus = status

    def getTradeModel(self):
        return self._trdModel
        
    def getConfigData(self):
        return self._cfgModel.getConfig()

    # +++++++++++++++++++++++内部接口++++++++++++++++++++++++++++
    def _createCalc(self):
        strategyParam = {
            "InitialFunds": 1000000, #self._cfgModel.getInitialFunds(),        # 初始资金
            "StrategyName": 'TEST111', #self._strategy.getStrategyName(),        # 策略名称
            "StartTime"   : '2019-04-01' ,#self._cfgModel.getStartTime(),           # 回测开始时间
            "EndTime"     : '2019-04-17', #self._cfgModel.getEndTime(),             # 回测结束时间
            "Margin"      : 0.08,                                    # 保证金
            "Slippage"    : 0,                                       # 滑点
            "OpenRatio"   : 0.08,
            "CloseRatio"  : 0.08,
            "OpenFixed"   : 0,
            "CloseFixed"  : 0,
            "CloseTodayRatio": 0.08,
            "CloseTodayFixed": 0,
            "KLineType"   : 'M', #self._cfgModel.getKLineType(),                        # K线类型
            "KLineSlice"  : 1,                          # K线间隔（1， 2， 5）
            "TradeDot"    : 10,                         # 每手乘数
            "PriceTick"   : 0.01,                       # 最小变动价位
        }
        
        return CalcCenter(strategyParam, self.logger)

    def getCalcCenter(self):
        return self._calcCenter
        
    def initialize(self):
        '''加载完策略初始化函数之后再初始化'''
        self._qteModel.initialize()
        self._hisModel.initialize()
        self._trdModel.initialize()
        
    #++++++++++++++++++++++策略接口++++++++++++++++++++++++++++++
    #//////////////////////历史行情接口//////////////////////////
    def runReport(self, context, handle_data):
        self._hisModel.runReport(context, handle_data)
        
    def runRealTime(self, context, handle_data, event):
        code = event.getEventCode()
        if code == ST_TRIGGER_KLINE:
            self._hisModel.runRealTime(context, handle_data, event)
        elif code == ST_TRIGGER_FILL_DATA:
            self._hisModel.runReportRealTime(context, handle_data, event)
                
    def reqHisQuote(self):
        self._hisModel.reqHisQuote()

    def onHisQuoteRsp(self, event):
        self._hisModel.onHisQuoteRsp(event)
        
    def onHisQuoteNotice(self, event):
        self._hisModel.onHisQuoteNotice(event)

    #///////////////////////即时行情接口//////////////////////////
    def reqExchange(self):
        self._qteModel.reqExchange()

    def reqCommodity(self):
        self._qteModel.reqCommodity()
        
    def subQuote(self):
        self._qteModel.subQuote()

    def onExchange(self, event):
        self._qteModel.onExchange(event)

    def onCommodity(self, event):
        self._qteModel.onCommodity(event)
            
    def onQuoteRsp(self, event):
        self._qteModel.onQuoteRsp(event)
        
    def onQuoteNotice(self, event):
        self._qteModel.onQuoteNotice(event)
        
    def onDepthNotice(self, event):
        self._qteModel.onDepthNotice(event)

    # ///////////////////////交易数据接口/////////////////////////
    def reqTradeData(self):
        self._trdModel.reqTradeData()
        
    #////////////////////////配置接口////////////////////////////
    def continueTrigger(self):
        return self._cfgModel.continues()

    #++++++++++++++++++++++base api接口++++++++++++++++++++++++++
    #////////////////////////K线函数/////////////////////////////
    def getBarOpen(self, symbol):
        return self._hisModel.getBarOpen(symbol)
        
    def getBarClose(self, symbol):
        return self._hisModel.getBarClose(symbol)
        
    def getBarHigh(self, symbol):
        return self._hisModel.getBarHigh(symbol)
        
    def getBarLow(self, symbol):
        return self._hisModel.getBarLow(symbol)

    # ////////////////////////即时行情////////////////////////////
    def getQAskPrice(self, symbol, level):
        return self._qteModel.getQAskPrice(symbol, level)

    def getQAskPriceFlag(self, symbol):
        return self._qteModel.getQAskPriceFlag(symbol)

    def getQAskVol(self, symbol, level):
        return self._qteModel.getQAskVol(symbol, level)

    def getQAvgPrice(self, symbol):
        return self._qteModel.getQAvgPrice(symbol)

    def getQBidPrice(self, symbol, level):
        return self._qteModel.getQBidPrice(symbol, level)

    def getQBidPriceFlag(self, symbol):
        return self._qteModel.getQBidPriceFlag(symbol)

    def getQBidVol(self, symbol, level):
        return self._qteModel.getQBidVol(symbol, level)

    def getQClose(self, symbol):
        return self._qteModel.getQClose(symbol)

    def getQHigh(self, symbol):
        return self._qteModel.getQHigh(symbol)

    def getQHisHigh(self, symbol):
        return self._qteModel.getQHisHigh(symbol)

    def getQHisLow(self, symbol):
        return self._qteModel.getQHisLow(symbol)

    def getQInsideVol(self, symbol):
        return self._qteModel.getQInsideVol(symbol)

    def getQLast(self, symbol):
        return self._qteModel.getQLast(symbol)

    def getQLastDate(self, symbol):
        return self._qteModel.getQLastDate(symbol)

    def getQLastFlag(self, symbol):
        return self._qteModel.getQLastFlag(symbol)

    def getQLastTime(self, symbol):
        return self._qteModel.getQLastTime(symbol)

    def getQLastVol(self, symbol):
        return self._qteModel.getQLastVol(symbol)

    def getQLow(self, symbol):
        return self._qteModel.getQLow(symbol)

    def getQLowLimit(self, symbol):
        return self._qteModel.getQLowLimit(symbol)

    def getQOpen(self, symbol):
        return self._qteModel.getQOpen(symbol)

    def getQOpenInt(self, symbol):
        return self._qteModel.getQOpenInt(symbol)

    def getQOpenIntFlag(self, symbol):
        return self._qteModel.getQOpenIntFlag(symbol)

    def getQOutsideVol(self, symbol):
        return self._qteModel.getQOutsideVol(symbol)

    def getQPreOpenInt(self, symbol):
        return self._qteModel.getQPreOpenInt(symbol)

    def getQPreSettlePrice(self, symbol):
        return self._qteModel.getQPreSettlePrice(symbol)

    def getQPriceChg(self, symbol):
        return self._qteModel.getQPriceChg(symbol)

    def getQPriceChgRadio(self, symbol):
        return self._qteModel.getQPriceChgRadio(symbol)

    def getQTodayEntryVol(self, symbol):
        return self._qteModel.getQTodayEntryVol(symbol)

    def getQTodayExitVol(self, symbol):
        return self._qteModel.getQTodayExitVol(symbol)

    def getQTotalVol(self, symbol):
        return self._qteModel.getQTotalVol(symbol)

    def getQTurnOver(self, symbol):
        return self._qteModel.getQTurnOver(symbol)

    def getQUpperLimit(self, symbol):
        return self._qteModel.getQUpperLimit(symbol)

    def getQuoteDataExist(self, symbol):
        return self._qteModel.getQuoteDataExist(symbol)

    # ////////////////////////策略函数////////////////////////////
    def setBuy(self, share, price):
        contNo = self._cfgModel.getBenchmark()
        curBar = self._hisModel.getCurBar()

        # 交易计算、生成回测报告
        # 产生信号
        userNo = self._cfgModel.getUserNo() if self._cfgModel.isActualRun() else "Default"
        orderParam = {
            "UserNo"          : userNo,                      # 账户编号
            "OrderType"       : otMarket,                     # 定单类型
            "ValidType"       : vtNone,                       # 有效类型
            "ValidTime"       : '0',                          # 有效日期时间(GTD情况下使用)
            "Cont"            : contNo,                       # 合约
            "Direct"          : dBuy,                         # 买卖方向：买、卖
            "Offset"          : oOpen,                        # 开仓、平仓、平今
            "Hedge"           : hSpeculate,                   # 投机套保
            "OrderPrice"      : price,                        # 委托价格 或 期权应价买入价格
            "OrderQty"        : share,                        # 委托数量 或 期权应价数量
            "DateTimeStamp"   : curBar['DateTimeStamp'],      # 时间戳（基准合约）
            "TradeDate"       : curBar['TradeDate'],          # 交易日（基准合约）
            "CurrentBarIndex" : curBar['KLineIndex'],         # 当前K线索引
        }
        self._calcCenter.addOrder(orderParam)
        self.sendSignalEvent("Buy", contNo, dBuy, oOpen, price, share, curBar)

        if self._cfgModel.isActualRun():
            self.sendOrder(userNo, contNo, otMarket, vtNone, dBuy, oOpen, hSpeculate, price, share)

    def setBuyToCover(self, share, price):
        contNo = self._cfgModel.getBenchmark()
        curBar = self._hisModel.getCurBar()

        # 交易计算、生成回测报告
        # 产生信号
        userNo = self._cfgModel.getUserNo() if self._cfgModel.isActualRun() else "Default"
        orderParam = {
            "UserNo"          : userNo,                      # 账户编号
            "OrderType"       : otMarket,                     # 定单类型
            "ValidType"       : vtNone,                       # 有效类型
            "ValidTime"       : '0',                          # 有效日期时间(GTD情况下使用)
            "Cont"            : contNo,                       # 合约
            "Direct"          : dBuy,                         # 买卖方向：买、卖
            "Offset"          : oCover,                       # 开仓、平仓、平今
            "Hedge"           : hSpeculate,                   # 投机套保
            "OrderPrice"      : price,                        # 委托价格 或 期权应价买入价格
            "OrderQty"        : share,                        # 委托数量 或 期权应价数量
            "DateTimeStamp"   : curBar['DateTimeStamp'],      # 时间戳（基准合约）
            "TradeDate"       : curBar['TradeDate'],          # 交易日（基准合约）
            "CurrentBarIndex" : curBar['KLineIndex'],         # 当前K线索引
        }

        self._calcCenter.addOrder(orderParam)
        self.sendSignalEvent("BuyToCover", contNo, dBuy, oCover, price, share, curBar)

        if self._cfgModel.isActualRun():
            self.sendOrder(userNo, contNo, otMarket, vtNone, dBuy, oCover, hSpeculate, price, share)

    def setSell(self, share, price):
        contNo = self._cfgModel.getBenchmark()
        curBar = self._hisModel.getCurBar()

        # 交易计算、生成回测报告
        # 产生信号
        userNo = self._cfgModel.getUserNo() if self._cfgModel.isActualRun() else "Default"
        orderParam = {
            "UserNo"          : userNo,                      # 账户编号
            "OrderType"       : otMarket,                     # 定单类型
            "ValidType"       : vtNone,                       # 有效类型
            "ValidTime"       : '0',                          # 有效日期时间(GTD情况下使用)
            "Cont"            : contNo,                       # 合约
            "Direct"          : dSell,                        # 买卖方向：买、卖
            "Offset"          : oCover,                       # 开仓、平仓、平今
            "Hedge"           : hSpeculate,                   # 投机套保
            "OrderPrice"      : price,                        # 委托价格 或 期权应价买入价格
            "OrderQty"        : share,                        # 委托数量 或 期权应价数量
            "DateTimeStamp"   : curBar['DateTimeStamp'],      # 时间戳（基准合约）
            "TradeDate"       : curBar['TradeDate'],          # 交易日（基准合约）
            "CurrentBarIndex" : curBar['KLineIndex'],         # 当前K线索引
        }
        self._calcCenter.addOrder(orderParam)
        self.sendSignalEvent("Sell", contNo, dSell, oCover, price, share, curBar)
        if self._cfgModel.isActualRun():
            self.sendOrder(userNo, contNo, otMarket, vtNone, dSell, oCover, hSpeculate, price, share)

    def setSellShort(self, share, price):
        contNo = self._cfgModel.getBenchmark()
        curBar = self._hisModel.getCurBar()

        #交易计算、生成回测报告
        #产生信号
        userNo = self._cfgModel.getUserNo() if self._cfgModel.isActualRun() else "Default"
        orderParam = {
            "UserNo"          : userNo,                      # 账户编号
            "OrderType"       : otMarket,                     # 定单类型
            "ValidType"       : vtNone,                       # 有效类型
            "ValidTime"       : '0',                          # 有效日期时间(GTD情况下使用)
            "Cont"            : contNo,                       # 合约
            "Direct"          : dSell,                        # 买卖方向：买、卖
            "Offset"          : oOpen,                        # 开仓、平仓、平今
            "Hedge"           : hSpeculate,                   # 投机套保
            "OrderPrice"      : price,                        # 委托价格 或 期权应价买入价格
            "OrderQty"        : share,                        # 委托数量 或 期权应价数量
            "DateTimeStamp"   : curBar['DateTimeStamp'],      # 时间戳（基准合约）
            "TradeDate"       : curBar['TradeDate'],          # 交易日（基准合约）
            "CurrentBarIndex" : curBar['KLineIndex'],         # 当前K线索引
        }
        self._calcCenter.addOrder(orderParam)
        self.sendSignalEvent("SellShort", contNo, dSell, oOpen, price, share, curBar)

        if self._cfgModel.isActualRun():
            self.sendOrder(userNo, contNo, otMarket, vtNone, dSell, oOpen, hSpeculate, price, share)

    def sendFlushEvent(self):
        flushEvent = Event({
            "EventCode": EV_ST2EG_UPDATE_STRATEGYDATA,
            "StrategyId": self._strategy.getStrategyId(),
        })
        self._strategy.sendEvent2Engine(flushEvent)

    def sendSignalEvent(self, signalName, contNo, direct, offset, price, share, curBar):
    
        data = [{
            'KLineIndex' : curBar['KLineIndex'],
            'ContractNo' : contNo,
            'Direct'     : direct,
            'Offset'     : offset,
            'Price'      : price,
            'Qty'        : share,
        }]

        #
        eventCode = EV_ST2EG_UPDATE_KLINESIGNAL if self._strategy.isRealTimeStatus() else EV_ST2EG_NOTICE_KLINESIGNAL
        signalNoticeEvent = Event({
            "EventCode": eventCode,
            "StrategyId": self._strategy.getStrategyId(),
            "Data": {
                'SeriesName': signalName,
                'Count': len(data),
                'Data': data,
            }
        })
        
        self._strategy.sendEvent2Engine(signalNoticeEvent)

    # def deleteOrder(self, contractNo):
    #     pass

    #////////////////////////设置函数////////////////////////////
    def getConfig(self):
        return self._cfgModel._metaData

    def setSetBenchmark(self, symbolTuple):
        self._cfgModel.setContract(symbolTuple)

    def setUserNo(self, userNo):
        self._cfgModel.setUserNo(userNo)

    def setAllKTrue(self):
        self._cfgModel.setAllKTrue()

    def setBarInterval(self, barType, barInterval):
        self._cfgModel.setBarInterval(barType, barInterval)

    def setBarPeriod(self, beginDate):
        if not beginDate:
            return -1
        self._cfgModel.setBarPeriod(beginDate)
        
    def setBarCount(self, count):
        self._cfgModel.setBarCount(count)

    def setInitCapital(self, capital):
        initFund = capital if capital else 1000000
        self._cfgModel.setInitCapital(initFund)
        return 0

    def setMargin(self, type, value):
        if not type or type not in (0, 1):
            return -1

        if type == 0:
            # 按比例
            if not value or value == 0:
                return self._cfgModel.setMargin('R', 0.08)

            if value > 1:
                return -1
            return self._cfgModel.setMargin('R', ())

        if type == 1:
            # 按固定值
            if not value or value <= 0:
                return -1
            return self._cfgModel.setMargin('F', value)

    def setTradeFee(self, type, rateFee, fixFee):
        '''
        :param type: 手续费类型，A-全部，O-开仓，C-平仓，T-平今
        :param rateFee: 按比例收取手续费，为0表示按定额收取
        :param fixFee: 按定额收取手续费，为0表示按比例收取，rateFee和fixFee都设置，按照fixFee * rateFee收取
        :return: 返回整型，0成功，-1失败
        '''
        if type not in ('A', 'O', 'C', 'T'):
            return -1

        if rateFee == 0 and fixFee == 0:
            return -1

        if rateFee < 0 or fixFee < 0:
            return -1

        if rateFee == 0:
            self._cfgModel.setTradeFee(type, 'F', fixFee)
            return 0

        if fixFee == 0:
            self._cfgModel.setTradeFee(type, 'R', rateFee)
            return 0

        self._cfgModel.setTradeFee(type, 'F', rateFee*fixFee)
        return 0

    def setTradeMode(self, inActual, sendOrderType, useSample, useReal):
        if sendOrderType not in (0, 1, 2):
            return -1

        self._cfgModel.setTradeMode(inActual, sendOrderType, useSample, useReal)
        return 0

    # ///////////////////////账户函数///////////////////////////
    def getAccountId(self):
        return self._trdModel.getAccountId()

    def getCost(self):
        return self._trdModel.getCost()

    def getCurrentEquity(self):
        return self._trdModel.getCurrentEquity()

    def getFreeMargin(self):
        return self._trdModel.getFreeMargin()

    def getProfitLoss(self):
        return self._trdModel.getProfitLoss()

    def getTotalFreeze(self):
        return self._trdModel.getTotalFreeze()

    def getBuyAvgPrice(self, contNo):
        return self._trdModel.getBuyAvgPrice(contNo)

    def getBuyPosition(self, contNo):
        return self._trdModel.getBuyPosition(contNo)

    def getBuyProfitLoss(self, contNo):
        return self._trdModel.getBuyProfitLoss(contNo)

    def getSellAvgPrice(self, contNo):
        return self._trdModel.getSellAvgPrice(contNo)

    def getSellPosition(self, contNo):
        return self._trdModel.getSellPosition(contNo)

    def getSellProfitLoss(self, contNo):
        return self._trdModel.getSellProfitLoss(contNo)

    def getTotalAvgPrice(self, contNo):
        return self._trdModel.getTotalAvgPrice(contNo)

    def getTotalPosition(self, contNo):
        return self._trdModel.getTotalPosition(contNo)

    def getTotalProfitLoss(self, contNo):
        return self._trdModel.getTotalProfitLoss(contNo)

    def getTodayBuyPosition(self, contNo):
        return self._trdModel.getTodayBuyPosition(contNo)

    def getTodaySellPosition(self, contNo):
        return self._trdModel.getTodaySellPosition(contNo)

    def getOrderBuyOrSell(self, eSession):
        return self._trdModel.getOrderBuyOrSell(eSession)

    def getOrderEntryOrExit(self, eSession):
        return self._trdModel.getOrderEntryOrExit(eSession)

    def getOrderFilledLot(self, eSession):
        return self._trdModel.getOrderFilledLot(eSession)

    def getOrderFilledPrice(self, eSession):
        return self._trdModel.getOrderFilledPrice(eSession)

    def getOrderLot(self, eSession):
        return self._trdModel.getOrderLot(eSession)

    def getOrderPrice(self, eSession):
        return self._trdModel.getOrderPrice(eSession)

    def getOrderStatus(self, eSession):
        return self._trdModel.getOrderStatus(eSession)

    def getOrderTime(self, eSession):
        return self._trdModel.getOrderTime(eSession)

    def sendOrder(self, userNo, contNo, orderType, validType, orderDirct, entryOrExit, hedge, orderPrice, orderQty):
        return self._trdModel.sendOrder(userNo, contNo, orderType, validType, orderDirct, entryOrExit, hedge, orderPrice, orderQty)

    def deleteOrder(self, eSession):
        return self._trdModel.deleteOrder(eSession)

    #///////////////////////绘图函数///////////////////////////
    def _addSeries(self, name, value, locator, color, barsback):
        addSeriesEvent = Event({
            "EventCode": EV_ST2EG_ADD_KLINESERIES,
            "StrategyId": self._strategy.getStrategyId(),
            "Data":{
                'ItemName':name,
                'Type': EEQU_INDICATOR,
                'Color': color,
                'Thick': 1,
                'OwnAxis': EEQU_ISNOT_AXIS,
                'Param': [],
                'ParamNum': 0,
                'Groupid': 0,
                'GroupName':name,
                'Main': EEQU_IS_MAIN,
            }
        })
        
        self._strategy.sendEvent2Engine(addSeriesEvent)
    
    def setPlotNumeric(self, name, value, locator, color, barsback):
        curBar = self._hisModel.getCurBar()
        
        if name not in self._plotedDict:
            self._addSeries(name, value, locator, color, barsback)
            self._plotedDict[name] = (name, value, locator, color, barsback)

        data = [{
            'KLineIndex' : curBar['KLineIndex'],
            'Value'      : value
        }]

        eventCode = EV_ST2EG_UPDATE_KLINESERIES if self._strategy.isRealTimeStatus() else EV_ST2EG_NOTICE_KLINESERIES
        serialEvent = Event({
            "EventCode" : eventCode,
            "StrategyId": self._strategy.getStrategyId(),
            "Data":{
                "SeriesName": name,
                "SeriesType": EEQU_INDICATOR,
                "IsMain"    : EEQU_IS_MAIN,
                "Count"     : len(data),
                "Data"      : data
            }
        })
        self._strategy.sendEvent2Engine(serialEvent)

    # ///////////////////////属性函数///////////////////////////
    def getBarInterval(self):
        if len(self._cfgModel._metaData) == 0 or 'Sample' not in self._cfgModel._metaData:
            return None

        sample = self._cfgModel.getSample()
        return sample['KLineSlice'] if 'KLineSlice' in sample else None

    def getBarType(self):
        if len(self._cfgModel._metaData) == 0 or 'Sample' not in self._cfgModel._metaData:
            return None

        sample = self._cfgModel.getSample()
        if 'KLineType' not in sample:
            return None

        return sample['KLineType']

    def getBidAskSize(self, contNo):
        contractNo = contNo
        if not contNo:
            contractTuple = self._cfgModel.getContract()
            if len(contractTuple) == 0:
                return 0
            else:
                contractNo = contractTuple[0]

        quoteModel = self._qteModel._contractData[contractNo]
        bidList = quoteModel._metaData['Lv2BidData']

        isNotAllZero = False
        for bidData in bidList:
            isNotAllZero = isNotAllZero or bidData != 0

        return len(bidList) if isNotAllZero else 0

    def getCommodityInfoFromContNo(self, contNo):
        '''
        从合约编号中提取交易所编码/商品编码/合约到期日期
        :param contNo: 合约编号
        :return: {}
        '''
        ret = {
            'ExchangeCode'  : '', # 交易所编码
            'CommodityCode' : '', # 商品编码
            'CommodityNo'   : '', # 合约到期日期
        }
        contractNo = contNo
        if not contNo:
            contractTuple = self._cfgModel.getContract()
            if len(contractTuple) == 0:
                return ret
            else:
                contractNo = contractTuple[0]

        contList = contractNo.split('|')
        if len(contList) == 0:
            return ret

        ret['ExchangeCode'] = contList[0]
        ret['CommodityCode'] = '|'.join(contList[:-1])
        ret['CommodityNo'] = contList[-1]
        return ret

    def getBigPointValue(self, contNo):
        commodityNo = self.getCommodityInfoFromContNo(contNo)['CommodityCode']


        if commodityNo not in self._qteModel._commodityData:
            return 0

        commodityModel = self._qteModel._commodityData[commodityNo]
        return commodityModel._metaData['PricePrec']

    def getCanTrade(self, contNo):
        return 0

    def getContractUnit(self, contNo):
        commodityNo = self.getCommodityInfoFromContNo(contNo)['CommodityCode']
        if commodityNo not in self._qteModel._commodityData:
            return 0

        commodityModel = self._qteModel._commodityData[commodityNo]
        return commodityModel._metaData['TradeDot']

    def getExchangeName(self, contNo):
        exchangeNo = self.getCommodityInfoFromContNo(contNo)['ExchangeCode']

        if exchangeNo not in self._qteModel._exchangeData:
            return None

        exchangeModel = self._qteModel._exchangeData[exchangeNo]
        return exchangeModel._metaData['ExchangeName']

    def getExpiredDate(self, contNo):
        return 0

    def getGetSessionCount(self, contNo):
        commodity = self.getCommodityInfoFromContNo(contNo)['CommodityCode']
        if commodity not in self._qteModel._commodityData:
            return 0

        sessionCount = 0
        timeBucket = self._qteModel._commodityData[commodity]._metaData['TimeBucket']
        for data in timeBucket:
            if data['TradeState'] == EEQU_TRADESTATE_CONTINUOUS:
                sessionCount += 1
        return sessionCount

    def getSessionEndTime(self, contNo, index):
        commodity = self.getCommodityInfoFromContNo(contNo)['CommodityCode']
        if commodity not in self._qteModel._commodityData:
            return 0

        timeBucket = self._qteModel._commodityData[commodity]._metaData['TimeBucket']
        return timeBucket[2*index + 1]["BeginTime"] if 2*index + 1 < len(timeBucket) else 0

    def getGetSessionStartTime(self, contNo, index):
        commodity = self.getCommodityInfoFromContNo(contNo)['CommodityCode']
        if commodity not in self._qteModel._commodityData:
            return 0

        timeBucket = self._qteModel._commodityData[commodity]._metaData['TimeBucket']
        return timeBucket[2 * index]["BeginTime"] if 2 * index < len(timeBucket) else 0

    def getMarginRatio(self, contNo):
        contractNo = contNo
        if not contNo:
            contractTuple = self._cfgModel.getContract()
            if len(contractTuple) == 0:
                return 0
            else:
                contractNo = contractTuple[0]

        marginValue = self._cfgModel.getMarginValue()
        return marginValue if not marginValue else 8

    def getMaxBarsBack(self):
        return self._hisModel.getHisLength()

    def getMaxSingleTradeSize(self):
        return MAXSINGLETRADESIZE

    def getMinMove(self, contNo):
        commodityNo = self.getCommodityInfoFromContNo(contNo)['CommodityCode']
        if commodityNo not in self._qteModel._commodityData:
            return 0

        commodityModel = self._qteModel._commodityData[commodityNo]
        priceTick = commodityModel._metaData['PriceTick']
        priceScale = commodityModel._metaData['PricePrec']
        return  priceTick/priceScale if priceScale != 0 else 0

    def getOptionStyle(self, contNo):
        return 0

    def getOptionType(self, contNo):
        contractNo = contNo
        if not contNo:
            contractTuple = self._cfgModel.getContract()
            if len(contractTuple) == 0:
                return -1
            else:
                contractNo = contractTuple[0]

        contInfo = contractNo.split('|')
        if len(contInfo) < 4 or contInfo[1] != EEQU_COMMODITYTYPE_OPTION:
            return -1

        commodityMo = contInfo[3]
        if 'C' in commodityMo or 'c' in commodityMo:
            return 0
        elif 'P' in commodityMo or 'p' in commodityMo:
            return 1
        return -1

    def getPriceScale(self, contNo):
        commodityNo = self.getCommodityInfoFromContNo(contNo)['CommodityCode']
        if commodityNo not in self._qteModel._commodityData:
            return 0

        commodityModel = self._qteModel._commodityData[commodityNo]
        return commodityModel._metaData['PricePrec']

    def getRelativeSymbol(self):
        return 0

    def getStrikePrice(self):
        return 0

    def getSymbol(self):
        return self._cfgModel.getContract()

    def getSymbolName(self, contNo):
        commodityInfo = self.getCommodityInfoFromContNo(contNo)
        commodityNo = commodityInfo['CommodityCode']
        if commodityNo not in self._qteModel._commodityData:
            return None

        commodityModel = self._qteModel._commodityData[commodityNo]
        commodityName = commodityModel._metaData['CommodityName']
        return commodityName+commodityInfo['CommodityNo']

    def getSymbolType(self, contNo):
        return self.getCommodityInfoFromContNo(contNo)['CommodityCode']


class StrategyConfig(object):
    '''
    功能：策略配置模块
    参数：
    {
        'Contract' : (  #合约设置,第一个元素为基准合约
            'ZCE|F|SR|905', 
        ),
        
        'Trigger'  : {  #触发方式设置
            '1' : '201904016100001'  定时触发       ST_TRIGGER_TIMER
            '2' : 300                周期触发(毫秒) ST_TRIGGER_CYCLE
            '3' : None,              K线触发        ST_TRIGGER_KLINE
            '4' : None,              即时行情触发   ST_TRIGGER_SANPSHOT
            '5' : None,              交易触发       ST_TRIGGER_TRADE
        },
        
        'Sample'   : {  #样本设置
            'KLineType'     : 'M',   K线类型
            'KLineSlice'    : 1,     K线周期
            'UseSample'     : True,  是否使用样本
            'KLineCount'    : 0,     K线数量
            'BeginTime'     : '',    起始日期， 目前支持到天
        },
        
        'RunMode'  : {  #运行模式
            'Simulate' : {
                'Continues' : True,  连续运行
            }
            'Actual'   : {
                'SendOrder' : '1'    发单模式,1-实时发单,2-K线完成后发单
            }
        },
        
        'Money'    : {   #资金设置
            'UserNo'    : 'ET001',    资金账号
            'InitFunds' : '1000000'   初始资金
            'OrderQty'  : {
                'Type'  : '1'-固定手数, '2'-固定资金，'3'-资金比例
                'Count' : 设置的值
            }
            'Hedge'     : T-投机,B-套保,S-套利,M-做市
            'MARGIN'    : {'Type':'F', 'Value':value} 'F'-固定值,'R'-比例
            'OpenFee'   : {'Type':'F', 'Value':value} 开仓手续费
            'CloseFee'  : {'Type':'F', 'Value':value} 平仓手续费
            'CloseTodayFee' : {'Type':'F', 'Value':value} 平今手续费
        }
        
        'Limit'   : {   #下单限制
            'OpenTimes' : 1, 每根K线同向开仓次数(-1,1-100)
            'ContinueOpenTimes' :-1, (-1, 1-100)
            'OpenAllowClose' : True  开仓的当前K线不允许平仓
            'CloseAllowOpen' : True  平仓的当前K线不允许开仓
        }
        
        'Other' : None                
      }
    '''
    def __init__(self, argsDict):
        
        ret = self._chkConfig(argsDict)
        if ret > 0:
            raise Exception(ret)
        
        self._metaData = deepcopy(argsDict)
        
    def _chkConfig(self, argsDict):
        if 'Contract' not in argsDict:
            return 1
            
        if 'Trigger' not in argsDict:
            return 2
            
        if 'Sample' not in argsDict:
            return 3
            
        if 'RunMode' not in argsDict:
            return 4 
            
        if 'Money' not in argsDict:
            return 5
            
        if 'Limit' not in argsDict:
            return 6
            
        return 0
        
    def continues(self):
        runModeDict = self.getRunMode()
        
        #实盘默认继续运行
        if 'Actual' in runModeDict:
            return True
            
        if 'Simulate' in runModeDict:
            return runModeDict['Simulate']['Continues']
        
        return False

    def getConfig(self):
        return self._metaData

    def getBenchmark(self):
        '''获取基准合约'''
        return self._metaData['Contract'][0]

    def setBenchmark(self, benchmark):
        '''设置基准合约'''
        if not benchmark:
            return 0

        if not self._metaData['Contract']:
            self._metaData['Contract'] = (benchmark, )

        contList = list(self._metaData['Contract'])
        contList[0] = benchmark
        self._metaData['Contract'] = tuple(contList)
        
    def getContract(self):
        '''获取合约列表'''
        return self._metaData['Contract']

    def setContract(self, contTuple):
        '''设置合约列表'''
        if not contTuple or not isinstance(contTuple, tuple):
            return 0
        self._metaData['Contract'] = contTuple

    def setUserNo(self, userNo):
        '''设置交易使用的账户'''
        if not userNo:
            self._metaData['Money']['UserNo'] = userNo
            return 0
        return -1

    def getUserNo(self):
        '''获取交易使用的账户'''
        return self._metaData['Money']['UserNo']

    def getTrigger(self):
        '''获取触发方式'''
        return self._metaData['Trigger']
        
    def getSample(self):
        '''获取样本数据'''
        return self._metaData['Sample']

    def setAllKTrue(self):
        '''使用所有K线回测'''
        sample = self._metaData['Sample']
        if 'BeginTime' in sample:
            del sample['BeginTime']

        if 'KLineCount' in sample:
            del sample['KLineCount']

        sample['AllK'] = True
        self._metaData['RunMode']['Simulate']['UseSample'] = True

    def setBarPeriod(self, beginDate):
        '''设置起止时间'''
        sample = self._metaData['Sample']
        if 'AllK' in sample:
            del sample['AllK']

        if 'KLineCount' in sample:
            del sample['KLineCount']

        sample['BeginTime'] = beginDate
        self._metaData['RunMode']['Simulate']['UseSample'] = True

    def setBarCount(self, count):
        '''设置K线数量'''
        sample = self._metaData['Sample']
        if 'AllK' in sample:
            del sample['AllK']

        if 'BeginTime' in sample:
            del sample['BeginTime']

        sample['KLineCount'] = count
        self._metaData['RunMode']['Simulate']['UseSample'] = True

    def setBarInterval(self, barType, barInterval):
        '''设置K线类型和K线周期'''
        if barType:
            self._metaData['Sample']['KLineType'] = barType
        if barInterval > 0:
            self._metaData['Sample']['KLineSlice'] = barInterval

    def getInitCapital(self):
        '''获取初始资金'''
        return self._metaData['Money']['InitFunds']

    def setInitCapital(self, capital):
        '''设置初始资金'''
        self._metaData['Money']['InitFunds'] = capital

    def getRunMode(self):
        '''获取运行模式'''
        return self._metaData['RunMode']

    def getMarginValue(self):
        '''获取保证金比例值'''
        return self._metaData['Money']['Margin']['Value']

    def getMarginType(self):
        '''获取保证金类型'''
        return self._metaData['Money']['Margin']['Type']

    def setMargin(self, type, value):
        '''设置保证金的类型及比例/额度'''
        if value < 0 or type not in ('R', 'F'):
            return -1

        self._metaData['Money']['Margin']['Value'] = value
        self._metaData['Money']['Margin']['Type'] = type
        return 0

    def setTradeFee(self, type, feeType, feeValue):
        typeMap = {
            'A' : {'OpenFee', 'CloseFee', 'CloseTodayFee'},
            'O' : {'OpenFee'},
            'C' : {'CloseFee'},
            'T' : {'CloseTodayFee'},
        }
        money = self._metaData['Money']
        if type in typeMap:
            keyDict = typeMap[type]
            for key in keyDict:
                moneyDict = money[key]
                moneyDict['Type'] = feeType
                moneyDict['Value'] = feeValue

    def setTradeMode(self, inActual, sendOrderType, useSample, useReal):
        if sendOrderType not in (0, 1, 2):
            return -1

        runMode = self._metaData['RunMode']
        if inActual:
            # 实盘运行
            runMode['Actual']['SendOrder2Actual'] = True
            runMode['SendOrder'] = sendOrderType
        else:
            # 模拟盘运行
            runMode['Simulate']['UseSample'] = useSample
            runMode['Simulate']['Continues'] = useReal


    def getSendOrder(self):
        return self._metaData['RunMode']['SendOrder']

    def isKLineTrigger(self):
        return bool(self._metaData['Trigger']['KLine'])

    def isActualRun(self):
        return bool(self._metaData['RunMode']['Actual']['SendOrder2Actual'])

class BarInfo(object):
    def __init__(self, logger):
        self._logger = logger
        self._barList = []
        self._curBar = None
        
    def _getBarValue(self, key):
        barValue = []
        for bar in self._barList:
            barValue.append(bar[key])
        return np.array(barValue)
    
    def updateBar(self, data):
        self._curBar = data
        self._barList.append(data)
        
    def getCurBar(self):
        return self._curBar
        
    def getBarOpen(self):
        return self._getBarValue('OpeningPrice')
        
    def getBarClose(self):
        return self._getBarValue('LastPrice')
        
    def getBarHigh(self):
        return self._getBarValue('HighPrice')
        
    def getBarLow(self):
        return self._getBarValue('LowPrice')
        
class StrategyHisQuote(object):
    '''
    功能：历史数据模型
    模型：
    _metaData = {
        'ZCE|F|SR|905' : 
        {
            'KLineReady' : False
            'KLineType'  : type
            'KLineSlice' : slice,
            'KLineData'  : [
                {
                    KLineIndex     : 0, 
                    TradeDate      : 20190405,
                    DateTimeStamp  : 20190405000000000,
                    TotalQty       : 1,
                    PositionQty    : 1,
                    LastPrice      : 4500,
                    KLineQty       : 1,
                    OpeningPrice   : 4500,
                    HighPrice      : 4500,
                    LowPrice       : 4500,
                    SettlePrice    : 4500,   
                },
                {
                    ...
                }
            ]
        }
        ...
    }
    '''
    def __init__(self, strategy, config, calc):
        # K线数据定义
        # response data
        self._metaData = {}
        self._earliestKLineDateTimeStamp = -1
        self._hisLength = 0
        #
        self._kLineNoticeData = {}

        self._strategy = strategy
        self.logger = strategy.logger
        self._config = config
        self._calc = calc
        
        # 运行位置的数据
        # 和存储位置的数据不一样，存储的数据 >= 运行的数据。
        self._curBarDict = {}
            
        # 请求次数，用于连续请求
        self._reqKLineTimes = 1

        # 按日期请求
        self._reqByDate = False
        self._reqBeginDate = 0

        # 上次时间戳
        self._lastTimestamp = 0
        
        # 回测阶段的实时K线数据,不出指标和信号
        self._reportRealDataList = []
        self._isAfterReportFirstData = True
        
    def initialize(self):
        self._contractTuple = self._config.getContract()
        
        # 基准合约
        self._contractNo = self._contractTuple[0]

        # 回测样本配置
        self._sampleDict = self._config.getSample()
        
        self._useSample = self._config.getRunMode()["Simulate"]["UseSample"]
        
        # 触发方式配置
        self._triggerDict = self._config.getTrigger()
        
        contractNo = self._config.getContract()[0]
        
        # Bar
        self._curBarDict[contractNo] = BarInfo(self.logger)

    # //////////////`////////////////////////////////////////////////////
    def getBorderIndex(self):
        return self._borderIndex

    def getHisLength(self):
        return self._hisLength
    # ////////////////////////BaseApi类接口////////////////////////

    def getBarOpen(self, contNo):
        if contNo == '':
            contNo = self._contractNo         
        return self._curBarDict[contNo].getBarOpen()
        
    def getBarClose(self, contNo):
        if contNo == '':
            contNo = self._contractNo
        return self._curBarDict[contNo].getBarClose()
        
    def getBarHigh(self, contNo):
        if contNo == '':
            contNo = self._contractNo
        return self._curBarDict[contNo].getBarHigh()
        
    def getBarLow(self, contNo):
        if contNo == '':
            contNo = self._contractNo
        return self._curBarDict[contNo].getBarLow()
        
    #////////////////////////参数设置类接口///////////////////////
        
    def _getKLineType(self):
        if not self._sampleDict:
            return None
        return self._sampleDict['KLineType']
        
    def _getKLineSlice(self):
        if not self._sampleDict:
            return None
        return self._sampleDict['KLineSlice']
        
    def _getKLineCount(self):
        #不使用历史K线，也要订阅1根
        if not self._useSample:
            return 1

        if 'KLineCount' in self._sampleDict:
            return self._sampleDict['KLineCount']

        if 'BeginTime' in self._sampleDict:
            return self._sampleDict['BeginTime']

        if 'AllK' in self._sampleDict:
            nowDateTime = datetime.now()
            if self._getKLineType() == EEQU_KLINE_DAY:
                threeYearsBeforeDateTime = nowDateTime - relativedelta(years = 3)
                threeYearsBeforeStr = datetime.strftime(threeYearsBeforeDateTime, "%Y%m%d")
                return threeYearsBeforeStr
            elif self._getKLineType() == EEQU_KLINE_HOUR or self._getKLineType() == EEQU_KLINE_MINUTE:
                oneMonthBeforeDateTime = nowDateTime - relativedelta(months = 1)
                oneMonthBeforeStr = datetime.strftime(oneMonthBeforeDateTime, "%Y%m%d")
                return oneMonthBeforeStr
            elif self._getKLineType() == EEQU_KLINE_SECOND:
                oneWeekBeforeDateTime = nowDateTime - relativedelta(days = 7)
                oneWeekBeforeStr = datetime.strftime(oneWeekBeforeDateTime, "%Y%m%d")
                return oneWeekBeforeStr
            else:
                raise NotImplementedError

    #//////////////////////////K线处理接口////////////////////////
    def reqKLinesByCount(self, contNo, count, notice):
        # print("请求k线", contNo, count)
        # 请求历史K线阶段先不订阅    
        event = Event({
            'EventCode'   : EV_ST2EG_SUB_HISQUOTE,
            'StrategyId'  : self._strategy.getStrategyId(),
            'ContractNo'  : contNo,
            'Data'        : {
                    'ReqCount'   :  count,
                    'ContractNo' :  contNo,
                    'KLineType'  :  self._getKLineType(),
                    'KLineSlice' :  self._getKLineSlice(),
                    'NeedNotice' :  EEQU_NOTICE_NEED
                },
            })
            
        self._strategy.sendEvent2Engine(event)

    def reqHisQuote(self):
        '''向9.5请求所有合约历史数据'''
        count, countOrDate = 0, self._getKLineCount()

        # print(" count or date is ", countOrDate)
        if isinstance(countOrDate, int):
            count = countOrDate
            self._reqByDate = False
        else:
            self._reqByDate = True
            #
            self._reaByDateEnd = False
            dateTimeStampLength = len("20190326143100000")
            self._reqBeginDate = int(countOrDate + (dateTimeStampLength-len(countOrDate))*'0')
            count = self._reqKLineTimes*4000

        self.reqKLinesByCount(self._contractNo, count, EEQU_NOTICE_NOTNEED)

    def onHisQuoteRsp(self, event):
        self._updateHisRspData(event)
        if self.isHisQuoteRspEnd(event):
            self._reIndexHisRspData()
            self._borderIndex = len(self._metaData[self._contractNo]["KLineData"])
            self._hisLength = len(self._metaData[self._contractNo]["KLineData"])

    def isHisQuoteRspEnd(self, event):
        if event.isChainEnd() and not self._reqByDate:
            return True
        if event.isChainEnd() and self._reqByDate and self._reqByDateEnd:
            return True
        return False

    # 更新response 数据
    def _updateHisRspData(self, event):
        contNo = event.getContractNo()
        if contNo not in self._metaData:
            self._metaData[contNo] = {
                'KLineReady': False,
                'KLineType': '',
                'KLineSlice': 1,
                'KLineData': [],
            }
        dataDict = self._metaData[contNo]
        dataDict['KLineType'] = event.getKLineType()
        dataDict['KLineSlice'] = event.getKLineSlice()
        rfdataList = dataDict['KLineData']

        dataList = event.getData()
        # print("datalist is ", dataList)
        for kLineData in dataList:
            if self._reqByDate:
                if len(rfdataList) == 0 or (len(rfdataList) >= 1 and kLineData["DateTimeStamp"] < rfdataList[0]["DateTimeStamp"] and \
                kLineData["DateTimeStamp"] >= self._reqBeginDate):
                    rfdataList.insert(0, kLineData)
            else:
                if len(rfdataList) == 0 or (len(rfdataList) >= 1 and kLineData["DateTimeStamp"] < rfdataList[0]["DateTimeStamp"]):
                    rfdataList.insert(0, kLineData)

        # print("rfdatalist length = ", len(rfdataList))
        # 如果是按照日期请求，指明是否继续请求
        if event.isChainEnd() and self._reqByDate:
            # 从9.5返回的数据为空的情况
            if len(rfdataList) == 0:
                self._reqByDateEnd = True
                self.logger.info("[HisQuote] response data is empty or not useful")
                return

            # print("本次请求k线开始时间:", rfdataList[0]["DateTimeStamp"])
            isNeedReqHisQuoteAgain = rfdataList[0]["DateTimeStamp"] > self._reqBeginDate
            self._reqByDateEnd = not isNeedReqHisQuoteAgain

            # 数据不够的情况
            if rfdataList[0]["DateTimeStamp"] != self._earliestKLineDateTimeStamp:
                self._earliestKLineDateTimeStamp = rfdataList[0]["DateTimeStamp"]
            else:
                isNeedReqHisQuoteAgain = False
                self._reqByDateEnd = True
            # ///////////////////////////////////////////////////////////////////
            if not self._reqByDateEnd:
                self._reqKLineTimes += 1
                self.reqKLinesByCount(self._contractNo, self._reqKLineTimes * 4000, EEQU_NOTICE_NOTNEED)

    def _reIndexHisRspData(self):
        dataDict = self._metaData[self._contractNo]
        rfdataList = dataDict['KLineData']
        dataDict['KLineReady'] = True
        for i, record in enumerate(rfdataList):
            rfdataList[i]['KLineIndex'] = i+1
            
    def _afterReportRealData(self, contNo):
        '''回测结束后，先发送回测阶段收到的实时数据，不发单'''
        for data in self._reportRealDataList:
            event = Event({
                "EventCode": ST_TRIGGER_FILL_DATA,
                "ContractNo": contNo,
                "Data":data
            })
            
            self._strategy.sendTriggerQueue(event)

    def onHisQuoteNotice(self, event):
        contNo = event.getContractNo()
        if contNo not in self._kLineNoticeData:
            self._kLineNoticeData[contNo] = {
                'KLineType' : '',
                'KLineSlice': 1,
                'KLineReady':True,
                'KLineData' : [],
            }
            self._borderIndex = 1
        dataDict = self._kLineNoticeData[contNo]
        dataDict['KLineType'] = event.getKLineType()
        dataDict['KLineSlice'] = event.getKLineSlice()
        rfdataList = dataDict['KLineData']

        dataList = event.getData()
        # notice数据，直接加到队尾
        for data in dataList:
            data["IsKLineStable"] = False
            #没有数据，索引取回测数据的最后一条数据的索引，没有数据从1开始
            if len(rfdataList) == 0:
                if contNo not in self._metaData:
                    data["KLineIndex"] = 1
                else:
                    reportKlineData = self._metaData[contNo]['KLineData']
                    data["KLineIndex"] = reportKlineData[-1]['KLineIndex']
            #该周期的tick更新数据，索引不变
            elif data["DateTimeStamp"] == rfdataList[-1]["DateTimeStamp"]:
                data["KLineIndex"] = rfdataList[-1]["KLineIndex"]
            #下个周期的数据，索引自增，标记K线稳定
            elif data["DateTimeStamp"] > rfdataList[-1]["DateTimeStamp"]:
                data["KLineIndex"] = rfdataList[-1]["KLineIndex"] + 1
                rfdataList[-1]["IsKLineStable"] = True

            #回测还没有结束，先保存数据
            if not self._strategy.isRealTimeStatus():
                self._reportRealDataList.append(data)
                #保证K线索引连续，数据也保存
                rfdataList.append(data)
                continue
                
            #回测结束，第一次收到数据,先发送回测阶段收到的实时数据，不发单
            if self._isAfterReportFirstData:
                self._afterReportRealData(contNo)
                self._isAfterReportFirstData = False
                
            orderWay = self._config.getSendOrder()
            
            isLastKLineStable = False
            if len(rfdataList) >= 1:
                isLastKLineStable = rfdataList[-1]["IsKLineStable"]
            
            #连续触发阶段，实时发单
            if orderWay == SendOrderRealTime:
                event = Event({
                    'EventCode': ST_TRIGGER_KLINE,
                    'ContractNo': contNo,
                    'Data': data
                })
                self._strategy.sendTriggerQueue(event)
            #K线稳定后发单，不考虑闭市最后一笔触发问题
            elif orderWay == SendOrderStable and isLastKLineStable:
                event = Event({
                    'EventCode'  : ST_TRIGGER_KLINE,
                    'ContractNo' : contNo,
                    'Data'       : rfdataList[-1],
                })
                self._strategy.sendTriggerQueue(event)
                
            rfdataList.append(data)

    # ///////////////////////////回测接口////////////////////////////////
    def _isAllReady(self):
        if not self._useSample:
            return True

        for contractNo in self._config.getContract():
            if contractNo not in self._metaData or not self._metaData[contractNo]["KLineReady"]:
                return False

        return True

    def _switchKLine(self, contNo):
        event = Event({
            "EventCode" :EV_ST2EG_SWITCH_STRATEGY,
            'StrategyId': self._strategy.getStrategyId(),
            'Data':
                {
                    'StrategyName': self._strategy.getStrategyName(),
                    'ContractNo'  : contNo,
                    'KLineType'   : self._getKLineType(),
                    'KLineSlice'  : self._getKLineSlice(),
                }
        })
        
        self._strategy.sendEvent2Engine(event)
        
    def _addKLine(self, data):
        event = Event({
            "EventCode"  : EV_ST2EG_NOTICE_KLINEDATA,
            "StrategyId" : self._strategy.getStrategyId(),
            "KLineType"  : self._getKLineType(),
            "Data": {
                'Count'  : 1,
                "Data"   : [data,],
            }
        })
        # print("历史回测阶段:", data["KLineIndex"])
        self._strategy.sendEvent2Engine(event)
        
    def _addSignal(self):
        event = Event({
            "EventCode"  :EV_ST2EG_ADD_KLINESIGNAL,
            'StrategyId' :self._strategy.getStrategyId(),
            "Data":{
                'ItemName':'EquantSignal',
                'Type': EEQU_INDICATOR,
                'Color': 0,
                'Thick': 1,
                'OwnAxis': EEQU_ISNOT_AXIS,
                'Param': [],
                'ParamNum': 0,
                'Groupid': 0,
                'GroupName':'Equant',
                'Main': EEQU_IS_MAIN,
            }
        })
        self._strategy.sendEvent2Engine(event)
    
    def _updateCurBar(self, contNo, data):
        '''更新当前Bar值'''
        self._curBarDict[contNo].updateBar(data)
        
    def _updateOtherBar(self, contNo, data):
        '''根据指定合约Bar值，更新其他合约bar值'''
        pass
    
    def _afterBar(self, contNo):
        barInfo = self.getCurBar(contNo)
        
        contPrices = [{
            "Cont"  : contNo,
            "Price" : barInfo['LastPrice'],     # 收盘价格
            "Time"  : barInfo["DateTimeStamp"],  # 当前时间戳
            "CurrentBarIndex"   : barInfo["KLineIndex"],  # 基准合约的bar索引
            "TradeDate"         : barInfo["TradeDate"],
         }]
        self._calc.calcProfit(contPrices, barInfo["DateTimeStamp"])
        result = self._calc.getMonResult()

        result.update({
            "StrategyName":self._strategy.getStrategyName(),
            "StrategyState":EEQU_STRATEGY_STATE_RUNNING,
        })

        event = Event({
            "EventCode":EV_EG2ST_MONITOR_INFO,
            "StrategyId":self._strategy.getStrategyId(),
            "Data":result
        })
        self._strategy.sendEvent2Engine(event)
        
    def _sendFlushEvent(self):
        event = Event({
            "EventCode": EV_ST2EG_UPDATE_STRATEGYDATA,
            "StrategyId": self._strategy.getStrategyId(),
        })
        self._strategy.sendEvent2Engine(event)
        
    def getCurBar(self, contNo = ''):
        if contNo == '':
            contNo = self._contractNo
        return self._curBarDict[contNo].getCurBar()
        
    def runReport(self, context, handle_data):
        '''历史回测接口'''
        # 不使用历史K线，也需要切换
        if not self._useSample:
            # 切换K线
            self._switchKLine(self._contractNo)
            # 增加信号线
            self._addSignal()
            self._sendFlushEvent()
            return

        while not self._isAllReady():
            time.sleep(1)
        # ==============使用基准合约回测==================
        # 切换K线
        self._switchKLine(self._contractNo)
        # # 增加信号线
        self._addSignal()
        # TODO: 基准合约和其他合约通过时间戳对应，暂时不考虑tick
        dataList = self._metaData[self._contractNo]['KLineData']

        self.logger.info('[runReport] run report begin')
        beginIndex = 0
        for i, data in enumerate(dataList):
            # 更新当前Bar
            self._updateCurBar(self._contractNo, data)
            # 根据基准合约，更新其他Bar
            self._updateOtherBar(self._contractNo, data)
            # 执行策略函数
            handle_data(context)
            # 通知当前Bar结束
            self._afterBar(self._contractNo)
            if i%200==0:
                self.drawBatchHisKine(dataList[beginIndex:i])
                beginIndex = i
                
        if beginIndex != len(dataList):
            self.drawBatchHisKine(dataList[beginIndex:])

        self.logger.debug('[runReport] run report completed!')
        # 回测完成，刷新信号、指标
        self._sendFlushEvent()

    def drawBatchHisKine(self, data):
        self.sendAllHisKLine(data)
        self._sendFlushEvent()

    def sendAllHisKLine(self, data):
        event = Event({
            "EventCode": EV_ST2EG_NOTICE_KLINEDATA,
            "StrategyId": self._strategy.getStrategyId(),
            "KLineType": self._getKLineType(),
            "Data": {
                'Count': len(data),
                "Data": data,
            }
        })
        self._strategy.sendEvent2Engine(event)
        
    def runReportRealTime(self, context, handle_data, event):
        '''发送回测阶段来的数据'''
        # 更新当前bar数据
        self._updateCurBar(contNo, data)
        self._updateOtherBar(contNo, data)
        # 推送K线
        self._updateRealTimeKLine(event.getData()) 

    def runRealTime(self, context, handle_data, event):
        '''K线实时触发'''
        contNo = event.getContractNo()
        data = event.getData()
        
        # 更新当前bar数据
        self._updateCurBar(contNo, data)
        self._updateOtherBar(contNo, data)
        # 推送K线
        self._updateRealTimeKLine(data)
        # 执行策略函数
        handle_data(context)
        # 通知当前Bar结束
        self._afterBar(contNo)
        self._sendFlushEvent()

    def _updateRealTimeKLine(self, data):
        event = Event({
            "EventCode": EV_ST2EG_UPDATE_KLINEDATA,
            "StrategyId": self._strategy.getStrategyId(),
            "KLineType": self._getKLineType(),
            "Data": {
                'Count': 1,
                "Data": [data, ],
            }
        })
        self._strategy.sendEvent2Engine(event)
    
class StrategyQuote(QuoteModel):
    '''即时行情数据模型'''
    def __init__(self, strategy, config):
        '''
        self._exchangeData  = {}  #{key=ExchangeNo,value=ExchangeModel}
        self._commodityData = {}  #{key=CommodityNo, value=CommodityModel}
        self._contractData  = {}  #{key=ContractNo, value=QuoteDataModel}
        '''
        self._strategy = strategy
        self.logger = strategy.logger
        QuoteModel.__init__(self, self.logger)
        self._config = config
        
    def initialize(self):
        self._contractTuple = self._config.getContract()
        
    def subQuote(self):
        contList = []
        for cno in self._contractTuple:
            contList.append(cno)

        event = Event({
            'EventCode'   : EV_ST2EG_SUB_QUOTE,
            'StrategyId'  : self._strategy.getStrategyId(),
            'Data'        : contList,
        })
            
        self._strategy.sendEvent2Engine(event) 

    def reqExchange(self):
        event = Event({
            'EventCode': EV_ST2EG_EXCHANGE_REQ,
            'StrategyId': self._strategy.getStrategyId(),
            'Data': '',
        })

        self._strategy.sendEvent2Engine(event)

    def reqCommodity(self):
        event = Event({
            'EventCode'   : EV_ST2EG_COMMODITY_REQ, 
            'StrategyId'  : self._strategy.getStrategyId(),
            'Data'        : '',
        })
        
        self._strategy.sendEvent2Engine(event)

    # /////////////////////////////应答消息处理///////////////////
    def onExchange(self, event):
        dataDict = event.getData()
        for k, v in dataDict.items():
            self._exchangeData[k] = ExchangeModel(self.logger, v)


    def onCommodity(self, event):
        dataDict = event.getData()
        for k, v in dataDict.items():
            self._commodityData[k] = CommodityModel(self.logger, v)

    def onQuoteRsp(self, event):
        '''
        event.Data = {
            'ExchangeNo' : dataDict['ExchangeNo'],
            'CommodityNo': dataDict['CommodityNo'],
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
        data = event.getData()

        if not isinstance(type(data), dict):
            return

        contractNo = apiEvent.getContractNo()
        if contractNo not in self._contractData:
            contMsg = {
                'ExchangeNo': data['ExchangeNo'],
                'CommodityNo': data['CommodityNo'],
                'ContractNo': contractNo,
            }
            self._contractData[contractNo] = QuoteDataModel(self.logger, contMsg)

        self._contractData[contractNo]._metaData = data

    def onQuoteNotice(self, event):
        QuoteModel.updateLv1(self, event)

    def onDepthNotice(self, event):
        QuoteModel.updateLv2(self, event)

    # ////////////////////////即时行情////////////////////////////
    # 参数验装饰器
    def paramValidatorFactory(abnormalRet):
        def paramValidator(func):
            def validator(*args, **kwargs):
                if len(args) == 0:
                    return abnormalRet
                if len(args) == 1:
                    return func(*args, **kwargs)

                model = args[0]
                contNo = args[1]
                if not contNo:
                    contNo = model._config.getBenchmark()

                if contNo not in model._contractData:
                    return abnormalRet
                elif not isinstance(model._contractData[contNo], QuoteDataModel):
                    return abnormalRet

                if len(args) == 2:
                    return func(model, contNo)

                if len(args) == 3:
                    if args[2] > 10:
                        return abnormalRet
                    return func(model, contNo, args[2])
            return validator
        return paramValidator

    # 合约最新卖价
    @paramValidatorFactory(0)
    def getQAskPrice(self, contNo, level=1):
        quoteDataModel = self._contractData[contNo]
        if level == 1:
            return quoteDataModel._metaData["Lv1Data"][17]

        lv2AskData = quoteDataModel._metaData["Lv2AskData"]
        if (level > len(lv2AskData)) or (not isinstance(lv2AskData[level-1], dict)):
            return 0

        return lv2AskData[level-1].get('Price')

    # 卖盘价格变化标志
    @paramValidatorFactory(0)
    def getQAskPriceFlag(self, contNo):
        # TODO: 增加卖盘价格比较逻辑
        return 1

    # 合约最新卖量
    @paramValidatorFactory(0)
    def getQAskVol(self, contNo, level=1):
        quoteDataModel = self._contractData[contNo]
        if level == 1:
            return quoteDataModel._metaData["Lv1Data"][18]

        lv2AskData = quoteDataModel._metaData["Lv2AskData"]
        if (level > len(lv2AskData)) or (not isinstance(lv2AskData[level - 1], dict)):
            return 0

        return lv2AskData[level - 1].get('Qty')

    # 实时均价即结算价
    @paramValidatorFactory(0)
    def getQAvgPrice(self, contNo):
        quoteDataModel = self._contractData[contNo]
        return quoteDataModel._metaData["Lv1Data"][15]

    # 合约最新买价
    @paramValidatorFactory(0)
    def getQBidPrice(self, contNo, level):
        quoteDataModel = self._contractData[contNo]
        if level == 1:
            return quoteDataModel._metaData["Lv1Data"][19]

        lv2BidData = quoteDataModel._metaData["Lv2BidData"]
        if (level > len(lv2BidData)) or (not isinstance(lv2BidData[level-1], dict)):
            return 0

        return lv2BidData[level-1].get('Price')

    # 买价变化标志
    @paramValidatorFactory(0)
    def getQBidPriceFlag(self, contNo):
        # TODO: 增加买价比较逻辑
        return 1

    # 指定合约,指定深度的最新买量
    @paramValidatorFactory(0)
    def getQBidVol(self, contNo, level):
        quoteDataModel = self._contractData[contNo]
        if level == 1:
            return quoteDataModel._metaData["Lv1Data"][20]

        lv2BidData = quoteDataModel._metaData["Lv2BidData"]
        if (level > len(lv2BidData)) or (not isinstance(lv2BidData[level - 1], dict)):
            return 0

        return lv2BidData[level - 1].get('Qty')

    # 当日收盘价，未收盘则取昨收盘
    @paramValidatorFactory(0)
    def getQClose(self, contNo):
        quoteDataModel = self._contractData[contNo]
        return quoteDataModel._metaData["Lv1Data"][0] if quoteDataModel._metaData["Lv1Data"][14] == 0 else quoteDataModel._metaData["Lv1Data"][14]

    # 当日最高价
    @paramValidatorFactory(0)
    def getQHigh(self, contNo):
        quoteDataModel = self._contractData[contNo]
        return quoteDataModel._metaData["Lv1Data"][5]

    # 历史最高价
    @paramValidatorFactory(0)
    def getQHisHigh(self, contNo):
        quoteDataModel = self._contractData[contNo]
        return quoteDataModel._metaData["Lv1Data"][7]

    # 历史最低价
    @paramValidatorFactory(0)
    def getQHisLow(self, contNo):
        quoteDataModel = self._contractData[contNo]
        return quoteDataModel._metaData["Lv1Data"][8]

    # 内盘量，买入价成交为内盘
    @paramValidatorFactory(0)
    def getQInsideVol(self, contNo):
        # TODO: 计算买入价成交量逻辑
        return 0

    # 最新价
    @paramValidatorFactory(0)
    def getQLast(self, contNo):
        quoteDataModel = self._contractData[contNo]
        return quoteDataModel._metaData["Lv1Data"][4]

    # 最新成交日期
    @paramValidatorFactory(None)
    def getQLastDate(self, contNo):
        # TODO: 获取最新成交日期逻辑
        return None

    # 最新价变化标志
    @paramValidatorFactory(0)
    def getQLastFlag(self, contNo):
        # TODO: 增加最新价和次最新价比较逻辑
        return 1

    # 最新成交时间
    @paramValidatorFactory(0)
    def getQLastTime(self, contNo):
        # TODO: 获取最新成交时间逻辑
        return None

    # 现手
    @paramValidatorFactory(0)
    def getQLastVol(self, contNo):
        # TODO: 增加现手计算逻辑
        return 0

    # 当日最低价
    @paramValidatorFactory(0)
    def getQLow(self, contNo):
        quoteDataModel = self._contractData[contNo]
        return quoteDataModel._metaData["Lv1Data"][6]

    # 当日跌停板价
    @paramValidatorFactory(0)
    def getQLowLimit(self, contNo):
        quoteDataModel = self._contractData[contNo]
        return quoteDataModel._metaData["Lv1Data"][10]

    # 当日开盘价
    @paramValidatorFactory(0)
    def getQOpen(self, contNo):
        quoteDataModel = self._contractData[contNo]
        return quoteDataModel._metaData["Lv1Data"][3]

    # 持仓量
    @paramValidatorFactory(0)
    def getQOpenInt(self, contNo):
        quoteDataModel = self._contractData[contNo]
        return quoteDataModel._metaData["Lv1Data"][12]

    # 持仓量变化标志
    @paramValidatorFactory(0)
    def getQOpenIntFlag(self, contNo):
        # TODO: 增加持仓量变化比较逻辑
        return 1

    # 外盘量
    @paramValidatorFactory(0)
    def getQOutsideVol(self, contNo):
        # TODO: 增加外盘量计算逻辑
        return 0

    # 昨持仓量
    @paramValidatorFactory(0)
    def getQPreOpenInt(self, contNo):
        quoteDataModel = self._contractData[contNo]
        return quoteDataModel._metaData["Lv1Data"][2]

    # 昨结算
    @paramValidatorFactory(0)
    def getQPreSettlePrice(self, contNo):
        quoteDataModel = self._contractData[contNo]
        return quoteDataModel._metaData["Lv1Data"][1]

    # 当日涨跌
    @paramValidatorFactory(0)
    def getQPriceChg(self, contNo):
        quoteDataModel = self._contractData[contNo]
        return quoteDataModel._metaData["Lv1Data"][112]

    # 当日涨跌幅
    @paramValidatorFactory(0)
    def getQPriceChgRadio(self, contNo):
        quoteDataModel = self._contractData[contNo]
        return quoteDataModel._metaData["Lv1Data"][113]

    # 当日开仓量
    @paramValidatorFactory(0)
    def getQTodayEntryVol(self, contNo):
        # TODO: 增加当日开仓量的计算逻辑
        return 0

    # 当日平仓量
    @paramValidatorFactory(0)
    def getQTodayExitVol(self, contNo):
        # TODO: 增加当日平仓量的计算逻辑
        return 0

    # 当日成交量
    @paramValidatorFactory(0)
    def getQTotalVol(self, contNo):
        quoteDataModel = self._contractData[contNo]
        return quoteDataModel._metaData["Lv1Data"][11]

    # 当日成交额
    @paramValidatorFactory(0)
    def getQTurnOver(self, contNo):
        quoteDataModel = self._contractData[contNo]
        return quoteDataModel._metaData["Lv1Data"][27]

    # 当日涨停板价
    @paramValidatorFactory(0)
    def getQUpperLimit(self, contNo):
        quoteDataModel = self._contractData[contNo]
        return quoteDataModel._metaData["Lv1Data"][9]

    # 行情数据是否有效
    @paramValidatorFactory(False)
    def getQuoteDataExist(self, contNo):
        quoteDataModel = self._contractData[contNo]
        return True if len(quoteDataModel._metaData["Lv1Data"]) else False


class StrategyTrade(TradeModel):
    '''交易数据模型'''
    def __init__(self, strategy, config):
        self.logger = strategy.logger
        self._strategy = strategy
        TradeModel.__init__(self, self.logger)
        self._config = config
        #self._selectedUserNo = self._config._metaData['Money']['UserNo']
        # print("===== StrategyTrade ====", self._config._metaData)

        # 本策略下的单
        # key 为 equant session id
        self._localOrder = {}
        # 本策略下单后，返回的结果
        # key 为 api session id
        # self._orderResult = {}

        # equant session id 到 api session id 的 映射
        # api session id 到 equant session id 的 映射
        self._eSessionId2apiSessionId = {}
        self._apiSessionId2ESessionId = {}
        
    def initialize(self):
        self._selectedUserNo = self._config.getUserNo()

    # 更新本地订单
    def updateEquantOrder(self, event):
        self._localOrder[event.getESessionId()] = event.getData()
        # print(" 本地订单id ",event.getESessionId())

    #
    def updateSessionIdMap(self, event):
        self._eSessionId2apiSessionId[event.getESessionId()] = event.getSessionId()
        # print(" 对应关系", event.getESessionId(), event.getSessionId())

    def reqTradeData(self):
        event = Event({
            'EventCode': EV_ST2EG_STRATEGYTRADEINFO,
            'StrategyId': self._strategy.getStrategyId(),
            'Data': '',
        })

        self._strategy.sendEvent2Engine(event)

    def getAccountId(self):
        '''
        :return:当前公式应用的交易帐户ID
        '''
        return self._selectedUserNo

    def getDataFromTMoneyModel(self, key):
        '''
        获取self._userInfo中当前账户指定的资金信息
        :param key:需要的资金信息的key
        :return:资金信息
        '''
        if len(self._userInfo) == 0 or self._selectedUserNo not in self._userInfo:
            return 0

        tUserInfoModel = self._userInfo[self._selectedUserNo]
        if len(tUserInfoModel._money) == 0:
            return 0

        tMoneyModel = None
        if 'Base' in tUserInfoModel._money:
            tMoneyModel = tUserInfoModel._money['Base']

        if len(tUserInfoModel._money) > 0:
            tMoneyModelList = list(tUserInfoModel._money.values())
            tMoneyModel = tMoneyModelList[0]

        if not tMoneyModel or key not in tMoneyModel._metaData:
            return 0

        return tMoneyModel._metaData[key]

    def getCost(self):
        '''
        :return: 当前公式应用的交易帐户的手续费
        '''
        return self.getDataFromTMoneyModel('Fee')

    def getCurrentEquity(self):
        '''
        :return:当前公式应用的交易帐户的动态权益
        '''
        return self.getDataFromTMoneyModel('Equity')

    def getFreeMargin(self):
        '''
        :return:当前公式应用的交易帐户的可用资金
        '''
        return self.getDataFromTMoneyModel('Available')

    def getProfitLoss(self):
        '''
        :return:当前公式应用的交易帐户的浮动盈亏
        '''
        return self.getDataFromTMoneyModel('FloatProfitTBT')

    def getTotalFreeze(self):
        '''
        :return:当前公式应用的交易帐户的冻结资金
        '''
        return self.getDataFromTMoneyModel('FrozenFee') + self.getDataFromTMoneyModel('FrozenDeposit')

    def getItemSumFromPositionModel(self, direct, contNo, key):
        '''
        获取某个账户下所有指定方向、指定合约的指标之和
        :param direct: 买卖方向，为空时表示所有方向
        :param contNo: 合约编号
        :param key: 指标名称
        :return:
        '''
        if len(self._userInfo) == 0 or self._selectedUserNo not in self._userInfo:
            return 0

        tUserInfoModel = self._userInfo[self._selectedUserNo]
        if len(tUserInfoModel._position) == 0:
            return 0

        contractNo = self._config._metaData['Contract'][0] if not contNo else contNo
        itemSum = 0.0
        for orderNo, tPositionModel in tUserInfoModel._position.items():
            if tPositionModel._metaData['Cont'] == contractNo and key in tPositionModel._metaData:
                if not direct or tPositionModel._metaData['Direct'] == direct:
                    itemSum += tPositionModel._metaData[key]

        return itemSum

    def getBuyAvgPrice(self, contNo):
        '''
        :return:当前公式应用的帐户下当前商品的买入持仓均价
        '''
        totalPosPrice = self.getItemSumFromPositionModel('B', contNo, 'PositionPrice')
        totalPosQty = self.getItemSumFromPositionModel('B', contNo, 'PositionQty')
        return totalPosPrice/totalPosQty if totalPosQty > 0 else 0

    def getBuyPosition(self, contNo):
        '''
        :return:当前公式应用的帐户下当前商品的买入持仓
        '''
        return self.getItemSumFromPositionModel('B', contNo, 'PositionQty')

    def getBuyProfitLoss(self, contNo):
        '''
        :return:当前公式应用的帐户下当前商品的买入持仓盈亏
        '''
        return self.getItemSumFromPositionModel('B', contNo, 'FloatProfit')

    def getSellAvgPrice(self, contNo):
        '''
        :return: 当前公式应用的帐户下当前商品的卖出持仓均价
        '''
        totalPosPrice = self.getItemSumFromPositionModel('S', contNo, 'PositionPrice')
        totalPosQty = self.getItemSumFromPositionModel('S', contNo, 'PositionQty')
        return totalPosPrice / totalPosQty if totalPosQty > 0 else 0

    def getSellPosition(self, contNo):
        '''
        :return: 当前公式应用的帐户下当前商品的卖出持仓
        '''
        return self.getItemSumFromPositionModel('S', contNo, 'PositionQty')

    def getSellProfitLoss(self, contNo):
        '''
        :return: 当前公式应用的帐户下当前商品的卖出持仓盈亏
        '''
        return self.getItemSumFromPositionModel('S', contNo, 'FloatProfit')

    def getTotalAvgPrice(self, contNo):
        '''
        :return: 当前公式应用的帐户下当前商品的持仓均价
        '''
        totalPosPrice = self.getItemSumFromPositionModel('', contNo, 'PositionPrice')
        totalPosQty = self.getItemSumFromPositionModel('', contNo, 'PositionQty')
        return totalPosPrice / totalPosQty if totalPosQty > 0 else 0

    def getTotalPosition(self, contNo):
        '''
        :return: 当前公式应用的帐户下当前商品的总持仓
        '''
        return self.getItemSumFromPositionModel('', contNo, 'PositionQty')

    def getTotalProfitLoss(self, contNo):
        '''
        :return: 当前公式应用的帐户下当前商品的总持仓盈亏
        '''
        return self.getItemSumFromPositionModel('', contNo, 'FloatProfit')

    def getTodayBuyPosition(self, contNo):
        '''
        :return: 当前公式应用的帐户下当前商品的当日买入持仓
        '''
        return self.getItemSumFromPositionModel('B', contNo, 'PositionQty') - self.getItemSumFromPositionModel('B', contNo, 'PrePositionQty')

    def getTodaySellPosition(self, contNo):
        '''
        :return: 当前公式应用的帐户下当前商品的当日卖出持仓
        '''
        return self.getItemSumFromPositionModel('S', contNo, 'PositionQty') - self.getItemSumFromPositionModel('S', contNo, 'PrePositionQty')

    def convertDateToTimeStamp(self, date):
        '''
        将日期转换为时间戳
        :param date: 日期
        :return:
        '''
        if not date:
            return 0

        struct_time = time.strptime(date, "%Y-%m-%d %H:%M:%S")
        timeStamp = time.mktime(struct_time)
        return timeStamp

    def getDataFromTOrderModel(self, orderNo, key):
        '''
        获取当前账号下的指定订单信息
        :param orderNo: 订单的委托编号，为空时，取最后提交的订单信息
        :param key: 指定信息对应的key，不可为空
        :return: 当前账号下的指定订单信息
        '''
        if not key:
            return 0

        if len(self._userInfo) == 0 or self._selectedUserNo not in self._userInfo:
            return 0

        tUserInfoModel = self._userInfo[self._selectedUserNo]

        if len(tUserInfoModel._order) == 0:
            return 0

        if orderNo and orderNo not in tUserInfoModel._order:
            return 0

        tOrderModel = None
        if not orderNo:
            # 委托单号 为空
            lastOrderTime = self.convertDateToTimeStamp('1970-01-01 08:00:00')
            for orderModel in tUserInfoModel._order.values():
                insertTimeStamp = self.convertDateToTimeStamp(orderModel._metaData['InsertTime'])
                updateTimeStamp = self.convertDateToTimeStamp(orderModel._metaData['UpdateTime'])
                orderTime = insertTimeStamp if insertTimeStamp >= updateTimeStamp else updateTimeStamp
                if orderTime > lastOrderTime:
                    lastOrderTime = orderTime
                    tOrderModel = orderModel
        else:
            tOrderModel = tUserInfoModel._order[orderNo]

        if not tOrderModel or key not in tOrderModel._metaData:
            return 0

        return tOrderModel._metaData[key]

    def getOrderBuyOrSell(self, eSession):
        '''
        返回当前公式应用的帐户下当前商品的某个委托单的买卖类型。
        :param orderNo: 委托单号，为空时，使用当日最后提交的委托编号作为查询依据
        :return: 当前公式应用的帐户下当前商品的某个委托单的买卖类型
        '''
        orderNo = self._strategy.getOrderNo(eSession)
        return self.getDataFromTOrderModel(orderNo, 'Direct')

    def getOrderEntryOrExit(self, eSession):
        '''
        返回当前公式应用的帐户下当前商品的某个委托单的开平仓状态
        :param orderNo: 委托单号，为空时，使用当日最后提交的委托编号作为查询依据
        :return: 当前公式应用的帐户下当前商品的某个委托单的开平仓状态
        '''
        orderNo = self._strategy.getOrderNo(eSession)
        return self.getDataFromTOrderModel(orderNo, 'Offset')

    def getDataFromTMatchModel(self, orderNo, key):
        '''
        获取当前账号下的指定成交信息
        :param orderNo: 订单的委托编号，为空时，取最后提交的订单信息
        :param key: 指定信息对应的key，不可为空
        :return: 当前账号下的指定成交信息
        '''

        if not key:
            return 0

        if len(self._userInfo) == 0 or self._selectedUserNo not in self._userInfo:
            return 0

        tUserInfoModel = self._userInfo[self._selectedUserNo]

        if len(tUserInfoModel._match) == 0:
            return 0

        if orderNo and orderNo not in tUserInfoModel._match:
            return 0

        tMatchModel = None
        if not orderNo:
            # 委托单号 为空
            lastMatchTime = self.convertDateToTimeStamp('1970-01-01 08:00:00')
            for matchModel in tUserInfoModel._match.values():
                matchTime = self.convertDateToTimeStamp(matchModel._metaData['MatchDateTime'])
                if matchTime > lastMatchTime:
                    lastMatchTime = matchTime
                    tMatchModel = matchModel
        else:
            tMatchModel = tUserInfoModel._order[orderNo]

        if not tMatchModel or key not in tMatchModel._metaData:
            return 0

        return tMatchModel._metaData[key]

    def getOrderFilledLot(self, eSession):
        '''
        返回当前公式应用的帐户下当前商品的某个委托单的成交数量
        :param orderNo: 委托单号，为空时，使用当日最后提交的委托编号作为查询依据
        :return: 当前公式应用的帐户下当前商品的某个委托单的成交数量
        '''
        orderNo = self._strategy.getOrderNo(eSession)
        return self.getDataFromTMatchModel(orderNo, 'MatchQty')

    def getOrderFilledPrice(self, eSession):
        '''
        返回当前公式应用的帐户下当前商品的某个委托单的成交价格
        :param orderNo: 委托单号，为空时，使用当日最后提交的委托编号作为查询依据
        :return: 当前公式应用的帐户下当前商品的某个委托单的成交价格
        '''
        orderNo = self._strategy.getOrderNo(eSession)
        return self.getDataFromTMatchModel(orderNo, 'MatchPrice')

    def getOrderLot(self, eSession):
        '''
        返回当前公式应用的帐户下当前商品的某个委托单的委托数量
        :param orderNo: 委托单号，为空时，使用当日最后提交的委托编号作为查询依据
        :return: 当前公式应用的帐户下当前商品的某个委托单的委托数量
        '''
        orderNo = self._strategy.getOrderNo(eSession)
        return self.getDataFromTOrderModel(orderNo, 'OrderQty')

    def getOrderPrice(self, eSession):
        '''
        返回当前公式应用的帐户下当前商品的某个委托单的委托价格
        :param orderNo: 委托单号，为空时，使用当日最后提交的委托编号作为查询依据
        :return: 当前公式应用的帐户下当前商品的某个委托单的委托价格
        '''
        orderNo = self._strategy.getOrderNo(eSession)
        return self.getDataFromTOrderModel(orderNo, 'OrderPrice')

    def getOrderStatus(self, eSession):
        '''
        返回当前公式应用的帐户下当前商品的某个委托单的状态
        :param orderNo: 委托单号，为空时，使用当日最后提交的委托编号作为查询依据
        :return: 当前公式应用的帐户下当前商品的某个委托单的状态
        '''
        orderNo = self._strategy.getOrderNo(eSession)
        return self.getDataFromTOrderModel(orderNo, 'OrderState')

    def getOrderTime(self, eSession):
        '''
        返回当前公式应用的帐户下当前商品的某个委托单的委托时间
        :param orderNo: 委托单号，为空时，使用当日最后提交的委托编号作为查询依据
        :return: 当前公式应用的帐户下当前商品的某个委托单的委托时间
        '''
        orderNo = self._strategy.getOrderNo(eSession)
        return self.getDataFromTOrderModel(orderNo, 'InsertTime')

    def sendOrder(self, userNo, contNo, orderType, validType, orderDirct, entryOrExit, hedge, orderPrice, orderQty):
        '''
        针对当前公式指定的帐户、商品发送委托单
        :param userNo: 指定的账户名
        :param contNo: 商品合约编号
        :param orderType: 订单类型
        :param validType: 订单有效类型
        :param orderDirct: 发送委托单的买卖类型，取值为Enum_Buy或Enum_Sell之一
        :param entryOrExit: 发送委托单的开平仓类型，取值为Enum_Entry,Enum_Exit,Enum_ExitToday之一
        :param hedge: 投保标记
        :param orderPrice: 委托单的交易价格
        :param orderQty: 委托单的交易数量
        :return: True/False
        '''
        if not userNo or not contNo or not orderType or not validType or not orderDirct or not entryOrExit or not hedge or not orderPrice or not orderQty:
            return -1

        if userNo not in self._userInfo:
            return -1

        # 获取资金账号
        userInfoModel = self._userInfo[userNo]
        sign = userInfoModel._metaData['Sign']
        aOrder = {
            'UserNo': userNo,
            'Sign': sign,
            'Cont': contNo,
            'OrderType': orderType,
            'ValidType': validType,
            'ValidTime': '0',
            'Direct': orderDirct,
            'Offset': entryOrExit,
            'Hedge': hedge,
            'OrderPrice': orderPrice,
            'TriggerPrice': 0,
            'TriggerMode': tmNone,
            'TriggerCondition': tcNone,
            'OrderQty': orderQty,
            'StrategyType': stNone,
            'Remark': '',
            'AddOneIsValid': tsDay,
        }

        eId = str(self._strategy.getStrategyId()) + '-' + str(self._strategy.getESessionId())
        aOrderEvent = Event({
            "EventCode": EV_ST2EG_ACTUAL_ORDER,
            "StrategyId": self._strategy.getStrategyId(),
            "Data": aOrder,
            "ESessionId": eId,
        })
        self._strategy.sendEvent2Engine(aOrderEvent)

        # 更新策略的订单信息
        self._strategy.setESessionId(self._strategy.getESessionId() + 1)
        self._strategy.updateLocalOrder(eId, aOrder)

        return eId

    def deleteOrder(self, eSession):
        '''
        针对当前公式应用的帐户、商品发送撤单指令。
        :param orderId: 所要撤委托单的定单号
        :return: 发送成功返回True, 发送失败返回False
        '''
        if not eSession:
            return False

        orderNo = self._strategy.getOrderNo(eSession)
        if not orderNo:
            return False

        orderId = None
        userNo = self._selectedUserNo
        userInfoModel = self._userInfo[userNo]
        for orderModel in userInfoModel._order.values():
            if orderModel._metaData['OrderNo'] == orderNo:
                orderId = orderModel._metaData['OrderId']

        if not orderId:
            return False

        aOrder = {
            "OrderId": orderId,
        }
        aOrderEvent = Event({
            "EventCode": EV_ST2EG_ACTUAL_CANCEL_ORDER,
            "StrategyId": self._strategy.getStrategyId(),
            "Data": aOrder
        })
        self._strategy.sendEvent2Engine(aOrderEvent)
        return True
