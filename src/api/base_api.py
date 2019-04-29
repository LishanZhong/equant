

#BaseApi类定义
class BaseApi(object):
    # 单例模式
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls)
            #print("create singleton instance of BaseAPI ", cls._instance)
        else:
            #print("BaseAPI instance has existed")
            pass
        return cls._instance

    def __init__(self, strategy = None, dataModel = None):
        self.updateData(strategy, dataModel)

    def updateData(self, strategy, dataModel):
        # 关联的策略
        self._strategy = strategy
        # 子进程数据模型
        self._dataModel = dataModel

    #/////////////////////////K线数据/////////////////////////////
    def Date(self):
        '''
        【说明】
              当前Bar的日期

        【语法】
              int Date()

        【参数】
              无

        【备注】
              简写D,返回格式为YYYYMMDD的整数

        【实例】
              当前Bar日期为2019-03-25,Date返回值为20190325
        '''
        return self._dataModel.getBarDate()

    def Time(self):
        '''
        【说明】
              当前Bar的时间

        【语法】
              float Time()

        【参数】
              无

        【备注】
              简写T, 返回格式为0.HHMMSSmmm的浮点数

        【实例】
              当前时间为11:34:21.356，Time返回值为0.113421356
        '''
        return self._dataModel.getBarTime()

    def Open(self, symbol=''):
        '''
        【说明】
              当前Bar的开盘价

        【语法】
              numpy.array Open()

        【参数】
              symbol 合约编号, 默认基准合约

        【备注】
              简写O, 返回值numpy数组包含截止当前Bar的所有开盘价
              Open()[-1] 表示当前Bar开盘价，Open()[-2]表示上一个Bar开盘价，以此类推

        【实例】
              Open() 获取基准合约的所有开盘价列表
              Open('ZCE|F|SR|905') 获取白糖905合约的所有开盘价列表
        '''
        return self._dataModel.getBarOpen(symbol)

    def High(self, symbol=''):
        '''
        【说明】
              当前Bar的最高价

        【语法】
              numpy.array High()

        【参数】
              symbol 合约编号,默认基准合约

        【备注】
              简写H, Tick时为当时的委托卖价
              返回numpy数组，包括截止当前Bar的所有最高价
              High()[-1] 表示当前Bar最高价，High()[-2]表示上一个Bar最高价，以此类推

        【实例】
              无
        '''
        return self._dataModel.getBarHigh(symbol)

    def Low(self, symbol=''):
        '''
        【说明】
              当前Bar的最低价

        【语法】
              numpy.array Low()

        【参数】
              symbol 合约编号, 默认基准合约

        【备注】
              简写H, Tick时为当时的委托卖价
              返回numpy数组，包括截止当前Bar的所有最低价
              Low()[-1] 表示当前Bar最低价，Low()[-2]表示上一个Bar最低价，以此类推

        【实例】
              无
        '''
        return self._dataModel.getBarLow(symbol)

    def Close(self, symbol):
        '''
        【说明】
              当前Bar的收盘价

        【语法】
              numpy.array Close()

        【参数】
              symbol 合约编号, 默认基准合约

        【备注】
              简写C, 返回numpy数组，包括截止当前Bar的所有收盘价
              Close()[-1] 表示当前Bar收盘价，Close()[-2]表示上一个Bar收盘价，以此类推

        【实例】
              无
        '''
        return self._dataModel.getBarClose(symbol)

    def Vol(self, symbol):
        '''
        【说明】
              当前Bar的成交量

        【语法】
              numpy.array Vol()

        【参数】
              symbol 合约编号, 默认基准合约

        【备注】
              简写V, 返回numpy数组，包括截止当前Bar的所有成交量
              Vol()[-1] 表示当前Bar成交量，Vol()[-2]表示上一个Bar成交量，以此类推

        【实例】
              无
        '''
        return self._dataModel.getBarVol(symbol)

    def OpenInt(self, symbol):
        '''
        【说明】
              当前Bar的持仓量

        【语法】
              numpy.array OpenInt()

        【参数】
              symbol 合约编号, 默认基准合约

        【备注】
              返回numpy数组，包括截止当前Bar的所有持仓量
              OpenInt()[-1] 表示当前Bar持仓量，OpenInt()[-2]表示上一个Bar持仓量，以此类推

        【实例】
              无
        '''
        return self._dataModel.getBarOpenInt(symbol)

    def TradeDate(self):
        '''
        【说明】
              当前Bar的交易日

        【语法】
              int TradeDate()

        【参数】
              无

        【备注】
              返回格式为YYYYMMDD的整数

        【实例】
              当前Bar日期为2019-03-25,Date返回值为20190325
        '''
        return self._dataModel.getBarTradeDate()

    def BarCount(self):
        '''
        【说明】
              当前合约Bar的总数

        【语法】
              int BarCount()

        【参数】
              无

        【备注】
              返回值为整型

        【实例】
              无
        '''
        return self._dataModel.getBarCount()

    def CurrentBar(self):
        '''
        【说明】
              当前Bar的索引值

        【语法】
              int CurrentBar()

        【参数】
              无

        【备注】
              第一个Bar返回值为0，其他Bar递增

        【实例】
              无
        '''
        return self._dataModel.getCurrentBar()

    def BarStatus(self):
        '''
        【说明】
              当前Bar的状态值

        【语法】
              int BarStatus()

        【参数】
              无

        【备注】
              返回值整型, 0表示第一个Bar,1表示中间普通Bar,2表示最后一个Bar

        【实例】
              无
        '''
        return self._dataModel.BarStatus()

    def HistoryDataExist(self):
        '''
        【说明】
              当前合约的历史数据是否有效

        【语法】
              int BarStatus()

        【参数】
              无

        【备注】
              返回Bool值，有效返回True，否则返回False

        【实例】
              无
        '''
        return self._dataModel.HistoryDataExist()

    #/////////////////////////即时行情/////////////////////////////
    def Q_AskPrice(self, symbol='', level=1):
        '''
        【说明】
              合约最新卖价

        【语法】
              float Q_AskPrice(string symbol, int level)

        【参数】
              symbol 合约编号, 默认当前合约;level 档位数,默认1档

        【备注】
              返回浮点数, 可获取指定合约,指定深度的最新卖价

        【实例】
              无
        '''
        return self._dataModel.getQAskPrice(symbol, level)


    def Q_AskPriceFlag(self, symbol=''):
        '''
        【说明】
              卖盘价格变化标志

        【语法】
              int Q_AskPriceFlag(string symbol)

        【参数】
              symbol 合约编号, 默认当前合约

        【备注】
              返回整型，1为上涨，-1为下跌，0为不变

        【实例】
              无
        '''
        return self._dataModel.getQAskPriceFlag(symbol)

    def Q_AskVol(self, symbol='', level=1):
        '''
        【说明】
              合约最新卖量

        【语法】
              float Q_AskVol(string symbol, int level)

        【参数】
              symbol 合约编号, 默认当前合约;level 档位数,默认1档

        【备注】
              返回浮点数, 可获取指定合约,指定深度的最新卖量

        【实例】
              无
        '''
        return self._dataModel.getQAskVol(symbol, level)

    def Q_AvgPrice(self, symbol=''):
        '''
        【说明】
              当前合约的历史数据是否有效

        【语法】
              float Q_AvgPrice(string symbol)

        【参数】
              symbol 合约编号, 默认当前合约

        【备注】
              返回浮点数，返回实时均价即结算价

        【实例】
              无
        '''
        return self._dataModel.getQAvgPrice(symbol)

    def Q_BidPrice(self, symbol='', level=1):
        '''
        【说明】
              合约最新买价

        【语法】
              float Q_BidPrice(string symbol, int level)

        【参数】
              symbol 合约编号, 默认当前合约;level 档位数,默认1档

        【备注】
              返回浮点数, 可获取指定合约,指定深度的最新买价

        【实例】
              无
        '''
        return self._dataModel.getQBidPrice(symbol, level)

    def Q_BidPriceFlag(self, symbol=''):
        '''
        【说明】
              买盘价格变化标志

        【语法】
              int Q_AskPriceFlag(string symbol)

        【参数】
              symbol 合约编号,  默认当前合约

        【备注】
              返回整型，1为上涨，-1为下跌，0为不变

        【实例】
              无
        '''
        return self._dataModel.getQBidPriceFlag(symbol)


    def Q_BidVol(self, symbol='', level=1):
        '''
        【说明】
              合约最新买量

        【语法】
              float Q_BidVol(string symbol, int level)

        【参数】
              symbol 合约编号, 默认当前合约;level 档位数,默认1档

        【备注】
              返回浮点数, 可获取指定合约,指定深度的最新买量

        【实例】
              无
        '''
        return self._dataModel.getQBidVol(symbol, level)

    def Q_Close(self, symbol=''):
        '''
        【说明】
              当日收盘价，未收盘则取昨收盘

        【语法】
              float Q_Close(string symbol)

        【参数】
              symbol 合约编号,默认当前合约

        【备注】
              返回浮点数

        【实例】
              无
        '''
        return self._dataModel.getQClose(symbol)

    def Q_High(self, symbol=''):
        '''
        【说明】
              当日最高价

        【语法】
              float Q_High(string symbol)

        【参数】
              symbol 合约编号

        【备注】
              返回浮点数

        【实例】
              无
        '''
        return self._dataModel.getQHigh(symbol)

    def Q_HisHigh(self, symbol=''):
        '''
        【说明】
              历史最高价

        【语法】
              float Q_HisHigh(string symbol)

        【参数】
              symbol 合约编号

        【备注】
              返回浮点数

        【实例】
              无
        '''
        return self._dataModel.getQHisHigh(symbol)

    def Q_HisLow(self, symbol=''):
        '''
        【说明】
              历史最低价

        【语法】
              float Q_HisLow(string symbol)

        【参数】
              symbol 合约编号

        【备注】
              返回浮点数

        【实例】
              无
        '''
        return self._dataModel.getQHisLow(symbol)

    def Q_InsideVol(self, symbol=''):
        '''
        【说明】
              内盘量

        【语法】
              float Q_InsideVol(string symbol)

        【参数】
              symbol 合约编号

        【备注】
              返回浮点数, 买入价成交为内盘

        【实例】
              无
        '''
        return self._dataModel.getQInsideVol(symbol)

    def Q_Last(self, symbol=''):
        '''
        【说明】
              最新价

        【语法】
              float Q_Last(string symbol)

        【参数】
              symbol 合约编号

        【备注】
              返回浮点数

        【实例】
              无
        '''
        return self._dataModel.getQLast(symbol)

    def Q_LastDate(self, symbol=''):
        '''
        【说明】
              最新成交日期

        【语法】
              int Q_LastDate(string symbol)

        【参数】
              symbol 合约编号

        【备注】
              返回Date类型

        【实例】
              无
        '''
        return self._dataModel.getQLastDate(symbol)

    def Q_LastFlag(self, symbol=''):
        '''
        【说明】
              最新价变化标志

        【语法】
              int Q_LastFlag(string symbol)

        【参数】
              symbol 合约编号

        【备注】
              返回整型, 1为上涨, -1为下跌, 0为不变

        【实例】
              无
        '''
        return self._dataModel.getQLastFlag(symbol)

    def Q_LastTime(self, symbol=''):
        '''
        【说明】
              最新成交时间

        【语法】
              float Q_LastTime(string symbol)

        【参数】
              symbol 合约编号

        【备注】
              返回Time类型

        【实例】
              无
        '''
        return self._dataModel.getQLastTime(symbol)

    def Q_LastVol(self, symbol=''):
        '''
        【说明】
              现手

        【语法】
              float Q_LastVol(string symbol)

        【参数】
              symbol 合约编号

        【备注】
              返回浮点数，单位为手

        【实例】
              无
        '''
        return self._dataModel.getQLastVol(symbol)

    def Q_Low(self, symbol=''):
        '''
        【说明】
              当日最低价

        【语法】
              float Q_Low(string symbol)

        【参数】
              symbol 合约编号

        【备注】
              返回浮点数

        【实例】
              无
        '''
        return self._dataModel.getQLow(symbol)

    def Q_LowLimit(self, symbol=''):
        '''
        【说明】
              当日跌停板价

        【语法】
              float Q_LowLimit(string symbol)

        【参数】
              symbol 合约编号

        【备注】
              返回浮点数

        【实例】
              无
        '''
        return self._dataModel.getQLowLimit(symbol)

    def Q_Open(self, symbol=''):
        '''
        【说明】
              当日开盘价

        【语法】
              float Q_Open(string symbol)

        【参数】
              symbol 合约编号

        【备注】
              返回浮点数

        【实例】
              无
        '''
        return self._dataModel.getQOpen(symbol)

    def Q_OpenInt(self, symbol=''):
        '''
        【说明】
              持仓量

        【语法】
              float Q_OpenInt(string symbol)

        【参数】
              symbol 合约编号

        【备注】
              返回浮点数, 单位为手

        【实例】
              无
        '''
        return self._dataModel.getQOpenInt(symbol)

    def Q_OpenIntFlag(self, symbol=''):
        '''
        【说明】
              持仓量变化标志

        【语法】
              int  Q_OpenIntFlag(string symbol)

        【参数】
              symbol 合约编号

        【备注】
              返回整型, 1为增加，-1为下降，0为不变

        【实例】
              无
        '''
        return self._dataModel.getQOpenIntFlag(symbol)

    def Q_OutsideVol(self, symbol=''):
        '''
        【说明】
              外盘量

        【语法】
              float Q_OutsideVol(string symbol)

        【参数】
              symbol 合约编号

        【备注】
              返回浮点数，卖出价成交为外盘

        【实例】
              无
        '''
        return self._dataModel.getQOutsideVol(symbol)

    def Q_PreOpenInt(self, symbol=''):
        '''
        【说明】
              昨持仓量

        【语法】
              float Q_PreOpenInt(string symbol)

        【参数】
              symbol 合约编号

        【备注】
              返回浮点数

        【实例】
              无
        '''
        return self._dataModel.getQPreOpenInt(symbol)

    def Q_PreSettlePrice(self, symbol=''):
        '''
        【说明】
              昨结算

        【语法】
              float Q_PreSettlePrice(string symbol)

        【参数】
              symbol 合约编号

        【备注】
              返回浮点数

        【实例】
              无
        '''
        return self._dataModel.getQPreSettlePrice(symbol)

    def Q_PriceChg(self, symbol=''):
        '''
        【说明】
              当日涨跌

        【语法】
              float Q_PriceChg(string symbol)

        【参数】
              symbol 合约编号

        【备注】
              返回浮点数

        【实例】
              无
        '''
        return self._dataModel.getQPriceChg(symbol)


    def Q_PriceChgRadio(self, symbol=''):
        '''
        【说明】
              当日涨跌幅

        【语法】
              float Q_PriceChgRadio(string symbol)

        【参数】
              symbol 合约编号

        【备注】
              返回浮点数

        【实例】
              无
        '''
        return self._dataModel.getQPriceChgRadio(symbol)

    def Q_TodayEntryVol(self, symbol=''):
        '''
        【说明】
              当日开仓量

        【语法】
              float Q_TodayEntryVol(string symbol)

        【参数】
              symbol 合约编号

        【备注】
              返回浮点数

        【实例】
              无
        '''
        return self._dataModel.getQTodayEntryVol(symbol)

    def Q_TodayExitVol(self, symbol=''):
        '''
        【说明】
              当日平仓量

        【语法】
              float Q_TodayExitVol(string symbol)

        【参数】
              symbol 合约编号

        【备注】
              返回浮点数

        【实例】
              无
        '''
        return self._dataModel.getQTodayExitVol(symbol)

    def Q_TotalVol(self, symbol=''):
        '''
        【说明】
              当日成交量

        【语法】
              float Q_TotalVol(string symbol)

        【参数】
              symbol 合约编号

        【备注】
              返回浮点数

        【实例】
              无
        '''
        return self._dataModel.getQTotalVol(symbol)

    def Q_TurnOver(self, symbol=''):
        '''
        【说明】
              当日成交额

        【语法】
              float Q_TurnOver(string symbol)

        【参数】
              symbol 合约编号

        【备注】
              返回浮点数

        【实例】
              无
        '''
        return self._dataModel.getQTurnOver(symbol)

    def Q_UpperLimit(self, symbol=''):
        '''
        【说明】
              当日涨停板价

        【语法】
              float Q_UpperLimit(string symbol)

        【参数】
              symbol 合约编号

        【备注】
              返回浮点数

        【实例】
              无
        '''
        return self._dataModel.getQUpperLimit(symbol)

    def QuoteDataExist(self, symbol=''):
        '''
        【说明】
              行情数据是否有效

        【语法】
              Bool QuoteDataExist(string symbol)

        【参数】
              symbol 合约编号

        【备注】
              返回Bool值，数据有效返回True，否则False

        【示例】
              无
        '''
        return self._dataModel.getQuoteDataExist(symbol)

    #/////////////////////////策略交易/////////////////////////////
    def Buy(self, share=0, price=0):
        '''
        【说明】
              产生一个多头建仓操作

        【语法】
              Bool Buy(int Share=0,float Price=0)

        【参数】
              Share 买入数量，为整型值，默认使用系统设置
              Price 买入价格，为浮点数，默认使用现价(非最后Bar为Close)。

        【备注】
              产生一个多头建仓操作，返回值为布尔型，执行成功返回True，否则返回False。
              该函数仅用于多头建仓，其处理规则如下：
              如果当前持仓状态为持平，该函数按照参数进行多头建仓。
              如果当前持仓状态为空仓，该函数平掉所有空仓，同时按照参数进行多头建仓，两个动作同时发出。
              如果当前持仓状态为多仓，该函数将继续建仓，但具体是否能够成功建仓要取决于系统中关于连续建仓的设置，以及资金，最大持仓量等限制。
              当委托价格超出k线的有效范围，在历史数据上，将会取最接近的有效价格发单；在实盘中，将会按照实际委托价格发单。
              例如：当前k线有效价格为50-100，用buy(1,10)发单，委托价将以50发单。

        【示例】
              在当前没有持仓或者持有多头仓位的情况下：
              Buy(50,10.2) 表示用10.2的价格买入50张合约。
              Buy(10,Close) 表示用当前Bar收盘价买入10张合约，马上发送委托。
              Buy(5,0) 表示用现价买入5张合约，马上发送委托。
              Buy(0,0) 表示用现价按交易设置中设置的手数,马上发送委托。

              在当前持有空头仓位的情况下：
              Buy(10,Close) 表示平掉所有空仓，并用当前Bar收盘价买入10张合约，马上发送委托。
        '''
        return self._dataModel.setBuy(share, price)

    def BuyToCover(self, share=0, price=0):
        '''
        【说明】
              产生一个空头平仓操作

        【语法】
              Bool BuyToCover(int Share=0,float Price=0)

        【参数】
              Share 买入数量，为整型值，默认为平掉当前所有持仓；
              Price 买入价格，为浮点数，默认=0时为使用现价(非最后Bar为Close)。

        【备注】
              产生一个空头平仓操作，返回值为布尔型，执行成功返回True，否则返回False。
              该函数仅用于空头平仓，其处理规则如下：
              如果当前持仓状态为持平，该函数不执行任何操作。
              如果当前持仓状态为多仓，该函数不执行任何操作。
              如果当前持仓状态为空仓，如果此时Share使用默认值，该函数将平掉所有空仓，达到持平的状态，否则只平掉参数Share的空仓。
              当委托价格超出k线的有效范围，在历史数据上，将会取最接近的有效价格发单；在实盘中，将会按照实际委托价格发单。
              例如：当前k线有效价格为50-100，用BuyToCover(1,10)发单，委托价将以50发单。

        【示例】
              在持有空头仓位的情况下：
              BuyToCover(50,10.2) 表示用10.2的价格空头买入50张合约。
              BuyToCover(10,Close) 表示用当前Bar收盘价空头买入10张合约，马上发送委托。
              BuyToCover(5,0) 表示用现价空头买入5张合约)，马上发送委托。
              BuyToCover(0,0) 表示用现价按交易设置中的设置,马上发送委托。
        '''
        return self._dataModel.setBuyToCover(share, price)

    def Sell(self, share=0, price=0):
        '''
        【说明】
              产生一个多头平仓操作

        【语法】
              Bool Sell(int Share=0,float Price=0)

        【参数】
              Share 卖出数量，为整型值，默认为平掉当前所有持仓；
              Price 卖出价格，为浮点数，默认=0时为使用现价(非最后Bar为Close)。

        【备注】
              产生一个多头平仓操作，返回值为布尔型，执行成功返回True，否则返回False。
              该函数仅用于多头平仓，其处理规则如下：
              如果当前持仓状态为持平，该函数不执行任何操作。
              如果当前持仓状态为空仓，该函数不执行任何操作。
              如果当前持仓状态为多仓，如果此时Share使用默认值，该函数将平掉所有多仓，达到持平的状态，否则只平掉参数Share的多仓。
              当委托价格超出k线的有效范围，在历史数据上，将会取最接近的有效价格发单；在实盘中，将会按照实际委托价格发单。
              例如：当前k线有效价格为50-100，用sell(1,10)发单，委托价将以50发单。

        【示例】
              在持有多头仓位的情况下：
              Sell(50,10.2) 表示用10.2的价格卖出50张合约。
              Sell(10,Close) 表示用当前Bar收盘价卖出10张合约，马上发送委托。
              Sell(5,0) 表示用现价卖出5张合约，马上发送委托。
              Sell(0,0) 表示用现价按交易设置中的设置,马上发送委托。
        '''
        return self._dataModel.setSell(share, price)

    def SellShort(self, share=0, price=0):
        '''
        【说明】
              产生一个空头建仓操作

        【语法】
              Bool SellShort(int Share=0,float Price=0)

        【参数】
              Share 卖出数量，为整型值，默认为使用系统设置参数；
              Price 卖出价格，为浮点数，默认=0时为使用现价(非最后Bar为Close)。

        【备注】
              产生一个空头建仓操作，返回值为布尔型，执行成功返回True，否则返回False。
              该函数仅用于空头建仓，其处理规则如下：
              如果当前持仓状态为持平，该函数按照参数进行空头建仓。
              如果当前持仓状态为多仓，该函数平掉所有多仓，同时按照参数进行空头建仓，两个动作同时发出
              如果当前持仓状态为空仓，该函数将继续建仓，但具体是否能够成功建仓要取决于系统中关于连续建仓的设置，以及资金，最大持仓量等限制。
              当委托价格超出k线的有效范围，在历史数据上，将会取最接近的有效价格发单；在实盘中，将会按照实际委托价格发单。
              例如：当前k线有效价格为50-100，用SellShort(1,10)发单，委托价将以50发单。

        【示例】
              在没有持仓或者持有空头持仓的情况下：
              SellShort(50,10.2) 表示用10.2的价格空头卖出50张合约。
              SellShort(10,Close) 表示用当前Bar收盘价空头卖出10张合约，马上发送委托。
              SellShort(5,0) 表示用现价空头卖出5张合约，马上发送委托。
              SellShort(0,0) 表示用现价按交易设置中设置的手数,马上发送委托。
              在MarketPosition=1的情况下：（当前持有多头持仓）
              SellShort(10,Close) 表示平掉所有多头仓位，并用当前Bar收盘价空头卖出10张合约，马上发送委托。

        '''
        return self._dataModel.setSellShort(share, price)
        
    #/////////////////////////属性函数/////////////////////////////
    def BarInterval(self):
        '''
        【说明】
              合约图表周期数值

        【语法】
              int BarInterval()

        【参数】
              无

        【备注】
              返回整型，通常和BarType一起使用进行数据周期的判别

        【示例】
              当前数据周期为1日线，BarInterval等于1；
              当前数据周期为22日线，BarInterval等于22；
              当前数据周期为60分钟线，BarInterval等于60；
              当前数据周期为1TICK线，BarInterval等于1；br> 当前数据周期为5000量线，BarInterval等于5000。
        '''
        return self._dataModel.getBarInterval()
        
    def BarType(self):
        '''
        【说明】
              合约图表周期类型值

        【语法】
              int BarType()

        【参数】
              无

        【备注】
              返回值为整型，通常和BarInterval一起使用进行数据周期的判别
              返回值如下定义：
              0 分时
              1 TICK线
              2 秒线
              3 分钟线
              4 小时线
              5 日线
              6 周线
              7 月线
              8 年线


        【示例】
              当前数据周期为22日线，BarType等于5；
              当前数据周期为60分钟线，BarType等于3；
              当前数据周期为1TICK线，BarType等于1；
              当前数据周期为3秒线，BarType等于2。
        '''
        return self._dataModel.getBarType()
        
    def BidAskSize(self, contNo):
        '''
        【说明】
              买卖盘个数

        【语法】
              int BidAskSize(contNo)

        【参数】
              contNo: 合约编号，为空时，取基准合约。

        【备注】
              返回整型

        【示例】
              郑商所白糖的买卖盘个数为5个，因此其BidAskSize等于5；
              郑商所棉花的买卖盘个数为1个，因此其BidAskSize等于1。 
        '''
        return self._dataModel.getBidAskSize(contNo)
        
    def BigPointValue(self, contNo):
        '''
        【说明】
              合约一个整数点的价值

        【语法】
              float BigPointValue(contNo)

        【参数】
              contNo: 合约编号，为空时，取基准合约。

        【备注】
              返回浮点数，1个整数点的价值，默认为1

        【示例】
              郑商所期货品种一个点的价值为1人民币，因此其BigPointValue等于1；
              港交所恒指期货一个点的价值为50港币，因此其BigPointValue等于50；
              CME E-MINI一个点的价值为50美元，因此其BigPointValue等于50； 
        '''
        return self._dataModel.getBigPointValue(contNo)

    def CanTrade(self, contNo):
        '''
        【说明】
              合约是否支持交易

        【语法】
              Bool CanTrade(contNo)

        【参数】
              contNo: 合约编号，为空时，取基准合约。

        【备注】
              返回Bool值，支持返回True，否则返回False

        【示例】
              无 
        '''
        return self._dataModel.getCanTrade(contNo)
        
    def ContractUnit(self, contNo):
        '''
        【说明】
              每张合约包含的基本单位数量, 即每手乘数

        【语法】
              int ContractUnit(contNo)

        【参数】
              contNo: 合约编号，为空时，取基准合约。

        【备注】
              返回整型，1张合约包含多少标底物。

        【示例】
              无 
        '''
        return self._dataModel.getContractUnit(contNo)
        
    def ExchangeName(self, contNo):
        '''
        【说明】
              合约对应交易所名称

        【语法】
              string ExchangeName(contNo)

        【参数】
              contNo: 合约编号，为空时，取基准合约。

        【备注】
              返回字符串

        【示例】
              郑商所下各合约的交易所名称为："郑州商品交易所"
        '''
        return self._dataModel.getExchangeName(contNo)
        
    def ExpiredDate(self, contNo):
        '''
        【说明】
              合约最后交易日

        【语法】
              string ExpiredDate(contNo)

        【参数】
              contNo: 合约编号，为空时，取基准合约。

        【备注】
              返回字符串

        【示例】
              无
        '''
        return self._dataModel.getExpiredDate()
        
    def GetSessionCount(self, contNo):
        '''
        【说明】
              获取交易时间段的个数

        【语法】
              int GetSessionCount(contNo)

        【参数】
              contNo: 合约编号，为空时，取基准合约。

        【备注】
              返回整型

        【示例】
              无
        '''
        return self._dataModel.getGetSessionCount(contNo)

    def GetSessionEndTime(self, contNo, index):
        '''
        【说明】
              获取指定交易时间段的结束时间。

        【语法】
              float GetSessionEndTime(contNo, index)

        【参数】
              contNo 合约编号，为空时，取基准合约。
              index 交易时间段的索引值, 从0开始。

        【备注】
              返回浮点数

        【示例】
              contNo = "ZCE|F|SR|905"
              sessionCount = GetSessionCount(contNo)
              for i in range(0, sessionCount-1):
                sessionEndTime = GetSessionEndTime(contNo, i)
        '''
        return self._dataModel.getSessionEndTime(contNo, index)

    def GetSessionStartTime(self, contNo, index):
        '''
        【说明】
              获取指定交易时间段的开始时间。

        【语法】
              float GetSessionStartTime(contNo, index)

        【参数】
              contNo 合约编号，为空时，取基准合约。
              index 交易时间段的索引值, 从0开始。

        【备注】
              返回浮点数

        【示例】
              无
        '''
        return self._dataModel.getGetSessionStartTime(contNo, index)

    def MarginRatio(self, contNo):
        '''
        【说明】
              获取合约默认保证金比率

        【语法】
              float MarginRatio()

        【参数】
              contNo 合约编号，为空时，取基准合约。

        【备注】
              返回浮点数

        【示例】
              无
        '''
        return self._dataModel.getMarginRatio(contNo)
        
    def MaxBarsBack(self):
        '''
        【说明】
              最大回溯Bar数

        【语法】
              float  MaxBarsBack()

        【参数】
              无

        【备注】
              返回浮点数

        【示例】
              无
        '''
        return self._dataModel.getMaxBarsBack()
        
    def MaxSingleTradeSize(self):
        '''
        【说明】
              单笔交易限量

        【语法】
              int MaxSingleTradeSize()

        【参数】
              无

        【备注】
              返回整型，单笔交易限量，对于不能交易的商品，返回-1，对于无限量的商品，返回0

        【示例】
              无
        '''
        return self._dataModel.getMaxSingleTradeSize()
        
    def MinMove(self, contNo):
        '''
        【说明】
              合约最小变动量

        【语法】
              int MinMove(contNo)

        【参数】
              contNo 合约编号，为空时，取基准合约。

        【备注】
              返回整型，MinMove = 最小变动价/ PriceScale

        【示例】
              沪铝的最小变动价为5，其PriceScale =1，因此其MinMove等于5
        '''
        return self._dataModel.getMinMove(contNo)
        
    def OptionStyle(self, contNo):
        '''
        【说明】
              期权类型，欧式还是美式

        【语法】
              int OptionStyle()

        【参数】
              contNo 合约编号，为空时，取基准合约。

        【备注】
              返回整型，0为欧式，1为美式

        【示例】
              无
        '''
        return self._dataModel.getOptionStyle(contNo)
        
    def OptionType(self, contNo):
        '''
        【说明】
              返回期权的类型，是看涨还是看跌期权

        【语法】
              int OptionType()

        【参数】
              无

        【备注】
              返回整型，0为看涨，1为看跌， -1为异常。

        【示例】
              无
        '''
        return self._dataModel.getOptionType(contNo)
        
    def PriceScale(self, contNo):
        '''
        【说明】
              合约价格精度

        【语法】
              float PriceScale()

        【参数】
              无

        【备注】
              返回浮点数

        【示例】
              上期沪金的报价精确到小数点2位，则PriceScale为1/100
        '''
        return self._dataModel.getPriceScale(contNo)
        
    def RelativeSymbol(self):
        '''
        【说明】
              关联合约

        【语法】
              string RelativeSymbol()

        【参数】
              无

        【备注】
              返回字符串
              主连或者近月合约，返回具体的某个月份的合约
              期权返回标的合约
              套利返回单腿合约，以逗号分隔
              其他，返回空字符串

        【示例】
              "ZCE|O|SR|905C5000"白糖期权的关联合约为"ZCE|F|SR|905"
              "SPD|m|OI/Y|001|001"菜油豆油价比的关联合约为"ZCE|F|OI|001,DCE|F|Y|001"
        '''
        return self._dataModel.getRelativeSymbol()
        
    def StrikePrice(self):
        '''
        【说明】
              获取期权行权价

        【语法】
              float StrikePrice()

        【参数】
              无

        【备注】
              返回浮点数

        【示例】
              无
        '''
        return self._dataModel.getStrikePrice()
        
    def Symbol(self):
        '''
        【说明】
              获取合约编号

        【语法】
              string Symbol()

        【参数】
              无

        【备注】
              期货、现货、指数: <EXG>|<TYPE>|<ROOT>|<YEAR><MONTH>[DAY]
              
              期权            : <EXG>|<TYPE>|<ROOT>|<YEAR><MONTH>[DAY]<CP><STRIKE>
              
              跨期套利        : <EXG>|<TYPE>|<ROOT>|<YEAR><MONTH>[DAY]|<YEAR><MONTH>[DAY]
              
              跨品种套利      : <EXG>|<TYPE>|<ROOT&ROOT>|<YEAR><MONTH>[DAY]
              
              极星跨期套利    : <EXG>|s|<ROOT>|<YEAR><MONTH>[DAY]|<YEAR><MONTH>[DAY]
              
              极星跨品种套利  : <EXG>|m|<ROOT-ROOT>|<YEAR><MONTH>|<YEAR><MONTH>
              
              极星现货期货套利: <EXG>|p|<ROOT-ROOT>||<YEAR><MONTH>

        【示例】
              "ZCE|F|SR|001", "ZCE|O|SR|001C5000"
        '''
        return self._dataModel.getSymbol()
        
    def SymbolName(self, contNo):
        '''
        【说明】
              获取合约名称

        【语法】
              string SymbolName()

        【参数】
              无

        【备注】
              返回字符串

        【示例】
              "ZCE|F|SR|001"的合约名称为"白糖001"
        '''
        return self._dataModel.getSymbolName(contNo)
        
    def SymbolType(self, contNo):
        '''
        【说明】
              获取合约所属的品种编号

        【语法】
              string SymbolType()

        【参数】
              无

        【备注】
              返回字符串

        【示例】
              "ZCE|F|SR|001"的品种编号为"ZCE|F|SR"
        '''
        return self._dataModel.getSymbolType(contNo)
        
    #////////////////////////////策略性能/////////////////

    #////////////////////////////账户函数/////////////////
    def A_AccountID(self):
        '''
        【说明】
              返回当前公式应用的交易帐户ID。

        【语法】
              string A_AccountID()

        【参数】
              无

        【备注】
              返回当前公式应用的交易帐户ID，返回值为字符串，无效时返回空串。
              注：不能使用于历史测试，仅适用于实时行情交易。

        【示例】
              无
        '''
        return self._dataModel.getAccountId()

    def A_Cost(self):
        '''
        【说明】
              返回当前公式应用的交易帐户的手续费。

        【语法】
              string A_Cost()

        【参数】
              无

        【备注】
              返回当前公式应用的交易帐户的手续费，返回值为浮点数。

        【示例】
              无
        '''
        return self._dataModel.getCost()

    def A_CurrentEquity(self):
        '''
        【说明】
              返回当前公式应用的交易帐户的动态权益。

        【语法】
              float A_CurrentEquity()

        【参数】
              无

        【备注】
              返回当前公式应用的交易帐户的动态权益，返回值为浮点数。

        【示例】
              无
        '''
        return self._dataModel.getCurrentEquity()

    def A_FreeMargin(self):
        '''
        【说明】
              返回当前公式应用的交易帐户的可用资金。

        【语法】
              float A_FreeMargin()

        【参数】
              无

        【备注】
              返回当前公式应用的交易帐户的可用资金，返回值为浮点数。
              注：不能使用于历史测试，仅适用于实时行情交易。

        【示例】
              无
        '''
        return self._dataModel.getFreeMargin()

    def A_ProfitLoss(self):
        '''
        【说明】
              返回当前公式应用的交易帐户的浮动盈亏。

        【语法】
              float A_ProfitLoss()

        【参数】
              无

        【备注】
              返回当前公式应用的交易帐户的浮动盈亏，返回值为浮点数。
              注：不能使用于历史测试，仅适用于实时行情交易。

        【示例】
              无
        '''
        return self._dataModel.getProfitLoss()

    def A_TotalFreeze(self):
        '''
        【说明】
              返回当前公式应用的交易帐户的冻结资金。

        【语法】
              float A_TotalFreeze()

        【参数】
              无

        【备注】
              返回当前公式应用的交易帐户的冻结资金，返回值为浮点数。
              注：不能使用于历史测试，仅适用于实时行情交易。

        【示例】
              无
        '''
        return self._dataModel.getTotalFreeze()

    def A_BuyAvgPrice(self, contNo):
        '''
        【说明】
              返回当前公式应用的帐户下当前商品的买入持仓均价。

        【语法】
              float A_BuyAvgPrice('ZCE|F|SR|905')

        【参数】
              contNo，指定商品的合约编号，
              为空时，采用基准合约编号。

        【备注】
              返回当前公式应用的帐户下当前商品的买入持仓均价，返回值为浮点数。
              注：不能使用于历史测试，仅适用于实时行情交易。

        【示例】
              无
         '''
        return self._dataModel.getBuyAvgPrice(contNo)

    def A_BuyPosition(self, contNo):
        '''
        【说明】
              返回当前公式应用的帐户下当前商品的买入持仓。

        【语法】
              float A_BuyPosition()

        【参数】
              contNo，指定商品的合约编号，
              为空时，采用基准合约编号。

        【备注】
              返回当前公式应用的帐户下当前商品的买入持仓，返回值为浮点数。
              注：不能使用于历史测试，仅适用于实时行情交易。

        【示例】
              当前持多仓2手，A_BuyPosition返回2。
         '''
        return self._dataModel.getBuyPosition(contNo)

    def A_BuyProfitLoss(self, contNo):
        '''
        【说明】
              返回当前公式应用的帐户下当前商品的买入持仓盈亏。

        【语法】
              float A_BuyProfitLoss()

        【参数】
              contNo，指定商品的合约编号，
              为空时，采用基准合约编号。

        【备注】
              返回当前公式应用的帐户下当前商品的买入持仓盈亏，返回值为浮点数。
              注：不能使用于历史测试，仅适用于实时行情交易。

        【示例】
              无
         '''
        return self._dataModel.getBuyProfitLoss(contNo)

    def A_SellAvgPrice(self, contNo):
        '''
        【说明】
              返回当前公式应用的帐户下当前商品的卖出持仓均价。

        【语法】
              float A_SellAvgPrice()

        【参数】
              contNo，指定商品的合约编号，
              为空时，采用基准合约编号。

        【备注】
              返回当前公式应用的帐户下当前商品的卖出持仓均价，返回值为浮点数。
              注：不能使用于历史测试，仅适用于实时行情交易。

        【示例】
              无
         '''
        return self._dataModel.getSellAvgPrice(contNo)

    def A_SellPosition(self, contNo):
        '''
        【说明】
              返回当前公式应用的帐户下当前商品的卖出持仓。

        【语法】
              float A_SellPosition()

        【参数】
              contNo，指定商品的合约编号，
              为空时，采用基准合约编号。

        【备注】
              返回当前公式应用的帐户下当前商品的卖出持仓，返回值为浮点数。
              注：不能使用于历史测试，仅适用于实时行情交易。

        【示例】
              当前持空仓3手，A_SellPosition返回3。
         '''
        return self._dataModel.getSellPosition(contNo)

    def A_SellProfitLoss(self, contNo):
        '''
        【说明】
              返回当前公式应用的帐户下当前商品的卖出持仓盈亏。

        【语法】
              float A_SellProfitLoss()

        【参数】
              contNo，指定商品的合约编号，
              为空时，采用基准合约编号。

        【备注】
              返回当前公式应用的帐户下当前商品的卖出持仓盈亏，返回值为浮点数。
              注：不能使用于历史测试，仅适用于实时行情交易。

        【示例】
              无
         '''
        return self._dataModel.getSellProfitLoss(contNo)

    def A_TotalAvgPrice(self, contNo):
        '''
        【说明】
              返回当前公式应用的帐户下当前商品的持仓均价。

        【语法】
              float A_TotalAvgPrice()

        【参数】
              contNo，指定商品的合约编号，
              为空时，采用基准合约编号。

        【备注】
              返回当前公式应用的帐户下当前商品的持仓均价，返回值为浮点数。
              注：不能使用于历史测试，仅适用于实时行情交易。

        【示例】
              无
         '''
        return self._dataModel.getTotalAvgPrice(contNo)

    def A_TotalPosition(self, contNo):
        '''
        【说明】
              返回当前公式应用的帐户下当前商品的总持仓。

        【语法】
              contNo，指定商品的合约编号，
              为空时，采用基准合约编号。

        【参数】
              无

        【备注】
              返回当前公式应用的帐户下当前商品的总持仓，返回值为浮点数。
              该持仓为所有持仓的合计值，正数表示多仓，负数表示空仓，零为无持仓。
              注：不能使用于历史测试，仅适用于实时行情交易。

        【示例】
              无
         '''
        return self._dataModel.getTotalPosition(contNo)

    def A_TotalProfitLoss(self, contNo):
        '''
        【说明】
              返回当前公式应用的帐户下当前商品的总持仓盈亏。

        【语法】
              float A_TotalProfitLoss()

        【参数】
              contNo，指定商品的合约编号，
              为空时，采用基准合约编号。

        【备注】
              返回当前公式应用的帐户下当前商品的总持仓盈亏，返回值为浮点数。
              注：不能使用于历史测试，仅适用于实时行情交易。

        【示例】
              无
         '''
        return self._dataModel.getTotalProfitLoss(contNo)

    def A_TodayBuyPosition(self, contNo):
        '''
        【说明】
              返回当前公式应用的帐户下当前商品的当日买入持仓。

        【语法】
              float A_TodayBuyPosition()

        【参数】
              contNo，指定商品的合约编号，
              为空时，采用基准合约编号。

        【备注】
              返回当前公式应用的帐户下当前商品的当日买入持仓，返回值为浮点数。
              注：不能使用于历史测试，仅适用于实时行情交易。

        【示例】
              无
         '''
        return self._dataModel.getTodayBuyPosition(contNo)

    def A_TodaySellPosition(self, contNo):
        '''
        【说明】
              返回当前公式应用的帐户下当前商品的当日卖出持仓。

        【语法】
              float A_TodaySellPosition()

        【参数】
              contNo，指定商品的合约编号，
              为空时，采用基准合约编号。

        【备注】
              返回当前公式应用的帐户下当前商品的当日卖出持仓，返回值为浮点数。
              注：不能使用于历史测试，仅适用于实时行情交易。

        【示例】
              无
         '''
        return self._dataModel.getTodaySellPosition(contNo)

    def A_OrderBuyOrSell(self, eSession):
        '''
        【说明】
              返回当前公式应用的帐户下当前商品的某个委托单的买卖类型。

        【语法】
              char A_OrderBuyOrSell(eSession)

        【参数】
              eSession 使用A_SendOrder返回的下单编号，
              eSession 为空时，使用当日最后成交的委托编号作为查询依据。

        【备注】
              返回当前公式应用的帐户下当前商品的某个委托单的买卖类型，返回值为：
              N : None
              B : 买入
              S : 卖出
              A : 双边
              该函数返回值可以与Enum_Buy、Enum_Sell等买卖状态枚举值进行比较，根据类型不同分别处理。
              注：不能使用于历史测试，仅适用于实时行情交易。

        【示例】
              nBorS = A_OrderBuyOrSell('1-1')
              if nBorS == Enum_Buy():
                ...
         '''
        return self._dataModel.getOrderBuyOrSell(eSession)

    def A_OrderEntryOrExit(self, eSession):
        '''
        【说明】
              返回当前公式应用的帐户下当前商品的某个委托单的开平仓状态。

        【语法】
              char A_OrderEntryOrExit(eSession)

        【参数】
              eSession 使用A_SendOrder返回的下单编号，
              eSession 为空时，使用当日最后成交的委托编号作为查询依据。

        【备注】
              返回当前公式应用的帐户下当前商品的某个委托单的开平仓状态，返回值：
              N : 无
              O : 开仓
              C : 平仓
              T : 平今
              1 : 开平，应价时有效, 本地套利也可以
              2 : 平开，应价时有效, 本地套利也可以
              该函数返回值可以与Enum_Entry、Enum_Exit等开平仓状态枚举值进行比较，根据类型不同分别处理。
              注：不能使用于历史测试，仅适用于实时行情交易。

        【示例】
              orderFlag = A_OrderEntryOrExit('1-1')
              if orderFlag == Enum_Exit():
                ...
         '''
        return self._dataModel.getOrderEntryOrExit(eSession)

    def A_OrderFilledLot(self, eSession):
        '''
        【说明】
              返回当前公式应用的帐户下当前商品的某个委托单的成交数量。

        【语法】
              float A_OrderFilledLot(orderNo)

        【参数】
              eSession 使用A_SendOrder返回的下单编号，
              eSession 为空时，使用当日最后成交的委托编号作为查询依据。

        【备注】
              返回当前公式应用的帐户下当前商品的某个委托单的成交数量，返回值为浮点数。
              注：不能使用于历史测试，仅适用于实时行情交易。

        【示例】
              无
         '''
        return self._dataModel.getOrderFilledLot(eSession)

    def A_OrderFilledPrice(self, eSession):
        '''
        【说明】
              返回当前公式应用的帐户下当前商品的某个委托单的成交价格。

        【语法】
              float A_OrderFilledPrice(eSession)

        【参数】
              eSession 使用A_SendOrder返回的下单编号，
              eSession 为空时，使用当日最后成交的委托编号作为查询依据。

        【备注】
              返回当前公式应用的帐户下当前商品的某个委托单的成交价格，返回值为浮点数。
              该成交价格可能为多个成交价格的平均值。
              注：不能使用于历史测试，仅适用于实时行情交易。

        【示例】
              无
         '''
        return self._dataModel.getOrderFilledPrice(eSession)

    def A_OrderLot(self, eSession):
        '''
        【说明】
              返回当前公式应用的帐户下当前商品的某个委托单的委托数量。

        【语法】
              float A_OrderLot(eSession)

        【参数】
              eSession 使用A_SendOrder返回的下单编号，
              eSession 为空时，使用当日最后成交的委托编号作为查询依据。

        【备注】
              返回当前公式应用的帐户下当前商品的某个委托单的委托数量，返回值为浮点数。
              注：不能使用于历史测试，仅适用于实时行情交易。

        【示例】
              无
         '''
        return self._dataModel.getOrderLot(eSession)

    def A_OrderPrice(self, eSession):
        '''
        【说明】
              返回当前公式应用的帐户下当前商品的某个委托单的委托价格。

        【语法】
              float A_OrderPrice(eSession)

        【参数】
              eSession 使用A_SendOrder返回的下单编号，
              eSession 为空时，使用当日最后成交的委托编号作为查询依据。

        【备注】
              返回当前公式应用的帐户下当前商品的某个委托单的委托价格，返回值为浮点数。
              注：不能使用于历史测试，仅适用于实时行情交易。

        【示例】
              无
         '''
        return self._dataModel.getOrderPrice(eSession)

    def A_OrderStatus(self, eSession):
        '''
        【说明】
              返回当前公式应用的帐户下当前商品的某个委托单的状态。

        【语法】
              char A_OrderStatus(eSession)

        【参数】
              eSession 使用A_SendOrder返回的下单编号，
              eSession 为空时，使用当日最后成交的委托编号作为查询依据。

        【备注】
              返回当前公式应用的帐户下当前商品的某个委托单的状态，返回值：
              N : 无
              0 : 已发送
              1 : 已受理
              2 : 待触发
              3 : 已生效
              4 : 已排队
              5 : 部分成交
              6 : 完全成交
              7 : 待撤
              8 : 待改
              9 : 已撤单
              A : 已撤余单
              B : 指令失败
              C : 待审核
              D : 已挂起
              E : 已申请
              F : 无效单
              G : 部分触发
              H : 完全触发
              I : 余单失败
              该函数返回值可以与委托状态枚举函数进行比较，根据类型不同分别处理。
              注：不能使用于历史测试，仅适用于实时行情交易。

        【示例】
              无
         '''
        return self._dataModel.getOrderStatus(eSession)

    def A_OrderTime(self, eSession):
        '''
        【说明】
              返回当前公式应用的帐户下当前商品的某个委托单的委托时间。

        【语法】
              struct_time A_OrderTime(eSession)

        【参数】
              eSession 使用A_SendOrder返回的下单编号，
              eSession 为空时，使用当日最后成交的委托编号作为查询依据。

        【备注】
              返回当前公式应用的帐户下当前商品的某个委托单的委托时间，返回值为格式化的时间。
              注：不能使用于历史测试，仅适用于实时行情交易。

        【示例】
              无
         '''
        return self._dataModel.getOrderTime(eSession)

    def A_SendOrder(self, userNo, contNo, orderType, validType, orderDirct, entryOrExit, hedge, orderPrice, orderQty):
        '''
        【说明】A_SendOrder
              针对指定的帐户、商品发送委托单。

        【语法】
              bool A_SendOrder(contNo, orderType, validType, orderDirct, entryOrExit, hedge, orderPrice, orderQty)

        【参数】
              userNo 指定的账户名称，
              contNo 商品合约编号，
              orderType 订单类型，字符类型，可选值为：
                '1' : 市价单
                '2' : 限价单
                '3' : 市价止损
                '4' : 限价止损
                '5' : 行权
                '6' : 弃权
                '7' : 询价
                '8' : 应价
                '9' : 冰山单
                'A' : 影子单
                'B' : 互换
                'C' : 套利申请
                'D' : 套保申请
                'F' : 行权前期权自对冲申请
                'G' : 履约期货自对冲申请
                'H' : 做市商留仓
              validType 订单有效类型，字符类型， 可选值为：
                '0' : 当日有效
                '1' : 长期有效
                '2' : 限期有效
                '3' : 即时部分
                '4' : 即时全部
              orderDirct 发送委托单的买卖类型，取值为Enum_Buy或Enum_Sell之一，
              entryOrExit 发送委托单的开平仓类型，取值为Enum_Entry,Enum_Exit,Enum_ExitToday之一，
              hedge 投保标记，字符类型，可选值为：
                'T' : 投机
                'B' : 套保
                'S' : 套利
                'M' : 做市
              orderPrice 委托单的交易价格，
              orderQty 委托单的交易数量。

        【备注】
              针对当前公式指定的帐户、商品发送委托单，发送成功返回如"1-1"的下单编号，发送失败返回-1。
              该函数直接发单，不经过任何确认，并会在每次公式计算时发送，一般需要配合着仓位头寸进行条件处理，在不清楚运行机制的情况下，请慎用。
              注：不能使用于历史测试，仅适用于实时行情交易。

        【示例】
              无
         '''
        return self._dataModel.sendOrder(userNo, contNo, orderType, validType, orderDirct, entryOrExit, hedge, orderPrice, orderQty)

    def A_DeleteOrder(self, eSession):
        '''
        【说明】
              针对当前公式应用的帐户、商品发送撤单指令。

        【语法】
              bool A_DeleteOrder(eSession)

        【参数】
              eSession 使用A_SendOrder返回的下单编号，
              eSession 为空时，使用当日最后成交的委托编号作为查询依据。

        【备注】
              针对当前公式应用的帐户、商品发送撤单指令，发送成功返回True, 发送失败返回False。
              该函数直接发单，不经过任何确认，并会在每次公式计算时发送，一般需要配合着仓位头寸进行条件处理，在不清楚运行机制的情况下，请慎用。
              注：不能使用于历史测试，仅适用于实时行情交易。

        【示例】
              无
         '''
        return self._dataModel.deleteOrder(eSession)

    #////////////////////////////绘图函数/////////////////
    def PlotNumeric(self, name, value, locator=0, color=-1, barsback=0):
        '''
        【说明】
              在当前Bar输出一个数值

        【语法】
              float PlotNumeric(string Name,float Value,float Locator=0,int Color=-1,int BarsBack=0)

        【参数】
              Name 输出值的名称，不区分大小写；
              Number 输出的数值；
              Locator 输出值的定位点，默认时输出单点，否则输出连接两个值线段，用法请看例3；
              Color 输出值的显示颜色，默认表示使用属性设置框中的颜色；
              BarsBack 从当前Bar向前回溯的Bar数，默认值为当前Bar。 

        【备注】
              在当前Bar输出一个数值，输出的值用于在上层调用模块显示。返回数值型，即输入的Number。

        【示例】
              例1：PlotNumeric ("MA1",Ma1Value);
              输出MA1的值。 
        '''
        return self._dataModel.setPlotNumeric(name, value, locator, color, barsback)
        
    #/////////////////////////////枚举函数/////////////////
    def Enum_Buy(self):
        '''
        【说明】
              返回买卖状态的买入枚举值

        【语法】
              int Enum_Buy()

        【参数】
              无

        【备注】
              返回整型

        【示例】
              无
        '''
        return self._dataModel.getEnumBuy()
        
    def Enum_Period_Tick(self):
        '''
        【说明】
              返回周期类型成交明细的枚举值

        【语法】
              int Enum_Period_Tick()

        【参数】
              无

        【备注】
              返回整型

        【示例】
              无
        '''
        return self._dataModel.getEnumPeriodTick()
        
    def Enum_Period_Dyna(self):
        '''
        【说明】
              返回周期类型分时图枚举值

        【语法】
              int Enum_Period_Dyna()

        【参数】
              无

        【备注】
              返回整型

        【示例】
              无
        '''
        return self._dataModel.getEnumPeriodDyna() 
        
    def Enum_Period_Second(self):
        '''
        【说明】
              返回周期类型秒线的枚举值

        【语法】
              int Enum_Period_Second()

        【参数】
              无

        【备注】
              返回整型

        【示例】
              无
        '''
        return self._dataModel.getEnumPeriodSecond() 
        
    def Enum_Period_Min(self):
        '''
        【说明】
              返回周期类型分钟线的枚举值

        【语法】
              int Enum_Period_Min()

        【参数】
              无

        【备注】
              返回整型

        【示例】
              无
        '''
        return self._dataModel.getEnumPeriodMin() 
        
    def Enum_Period_Hour(self):
        '''
        【说明】
              返回周期类型小时线的枚举值

        【语法】
              int Enum_Period_Hour()

        【参数】
              无

        【备注】
              返回整型

        【示例】
              无
        '''
        return self._dataModel.getEnumPeriodHour() 
        
    def Enum_Period_Day(self):
        '''
        【说明】
              返回周期类型日线的枚举值

        【语法】
              int Enum_Period_Day()

        【参数】
              无

        【备注】
              返回整型

        【示例】
              无
        '''
        return self._dataModel.getEnumPeriodDay() 
        
    def Enum_Period_Week(self):
        '''
        【说明】
              返回周期类型周线的枚举值

        【语法】
              int Enum_Period_Week()

        【参数】
              无

        【备注】
              返回整型

        【示例】
              无
        '''
        return self._dataModel.getEnumPeriodWeek()

    def Enum_Period_Month(self):
        '''
        【说明】
              返回周期类型月线的枚举值

        【语法】
              int Enum_Period_Month()

        【参数】
              无

        【备注】
              返回整型

        【示例】
              无
        '''
        return self._dataModel.getEnumPeriodMonth() 
    
    def Enum_Period_Year(self):
        '''
        【说明】
              返回周期类型年线的枚举值

        【语法】
              int Enum_Period_Year()

        【参数】
              无

        【备注】
              返回整型

        【示例】
              无
        '''
        return self._dataModel.getEnumPeriodYear() 

    def Enum_Period_DayX(self):
        '''
        【说明】
              返回周期类型多日线的枚举值

        【语法】
              int Enum_Period_DayX()

        【参数】
              无

        【备注】
              返回整型

        【示例】
              无
        '''
        return self._dataModel.getEnumPeriodDayX()   

    #//////////////////////设置函数////////////////////
    def GetConfig(self):
        return self._dataModel.getConfig()

    def SetBenchmark(self,symbolTuple):
        '''
        【说明】
              设置基准合约及相关联的合约列表

        【语法】
              int SetBenchmark(tuple symbolTuple)

        【参数】
              symbolTuple 元组，第一个元素为基准合约

        【备注】
              返回整型, 0成功，-1失败

        【示例】
              SetBenchmark(('ZCE|F|SR|905',))
              SetBenchmark(('ZCE|F|SR|905', 'ZCE|F|SR|912', 'ZCE|F|SR|001'))
        '''
        return self._dataModel.setSetBenchmark(symbolTuple)

    def SetUserNo(self, userNo):
        '''
        【说明】
              设置实盘交易账户

        【语法】
              int SetUserNo(str userNo)

        【参数】
              userNo 实盘交易账户

        【备注】
              返回整型, 0成功，-1失败

        【示例】
              SetUserNo('ET001')
        '''
        return self._dataModel.setUserNo(userNo)

    def SetBarInterval(self, barType, barInterval):
        '''
        【说明】
              设置K线类型和K线周期

        【语法】
              int SetBarInterval(int barType, int barInterval)

        【参数】
              barType K线类型 t分时，T分笔，S秒线，M分钟，H小时，D日线，W周线，m月线，Y年线
              barInterval K线周期

        【备注】
              返回整型, 0成功，-1失败

        【示例】
              SetBarInterval(3, 3) 表示3分钟线
        '''
        return self._dataModel.setBarInterval(barType, barInterval)

    def SetAllKTrue(self):
        '''
        【说明】
              使用所有历史K线进行历史回测

        【语法】
              int SetAllKTrue()

        【参数】
              无

        【备注】
              返回整型，0成功，-1失败

        【示例】
              SetAllKTrue()
        '''
        return self._dataModel.setAllKTrue()

    def SetBarPeriod(self, beginDate):
        '''
        【说明】
              设置K线范围，不设置年线、月线、周线、日线全部，分钟线1年，秒线1月，tick2天

        【语法】
              int SetBarPeriod(string beginDate)

        【参数】
              beginDate 起始日期

        【备注】
              返回整型，0成功，-1失败

        【示例】
              SetBarPeriod('20180327')
        '''
        return self._dataModel.setBarPeriod(beginDate)

    def SetBarCount(self, count):
        '''
        【说明】
              设置K线数量

        【语法】
              int SetBarCount(int count)

        【参数】
              count K线数量

        【备注】
              返回整型，0成功，-1失败

        【示例】
              SetBarCount(1000)
            
        '''
        return self._dataModel.setBarCount(count)
        
    def SetInitCapital(self, capital):
        '''
        【说明】
              设置初始资金，不设置默认100万

        【语法】
              int SetInitCapital(float capital)

        【参数】
              capital 初始资金

        【备注】
              返回整型，0成功，-1失败

        【示例】
              SetInitCapital(200*10000), 设置初始资金为200万
        '''
        return self._dataModel.setInitCapital(capital)
        
    def SetMargin(self, type, value):
        '''
        【说明】
              设置保证金参数，不设置取交易所公布参数

        【语法】
              int SetMargin(float type, float value)

        【参数】
              type 0：按比例收取保证金， 1：按定额收取保证金，
              value 按比例收取保证金时的比例， 或者按定额收取保证金时的额度。

        【备注】
              返回整型，0成功，-1失败

        【示例】
              SetMargin(0, 0.08) 设置保证金按比例收取8%
              SetMargin(1, 80000) 设置保证金按额度收取80000
        '''
        return self._dataModel.setMargin(type, value)
        
    def SetTradeFee(self, type, rateFee, fixFee):
        '''
        【说明】
              设置手续费收取方式，不设置取交易所公布参数

        【语法】
              int SetTradeFee(string type, float rateFee, float fixFee)

        【参数】
              type 手续费类型，A-全部，O-开仓，C-平仓，T-平今
              rateFee 按比例收取手续费，为0表示按定额收取
              fixFee 按定额收取手续费，为0表示按比例收取
              rateFee和fixFee都设置，按照fixFee * rateFee收取
        【备注】
              返回整型，0成功，-1失败

        【示例】
              SetTradeFee('O', 0, 5) 设置开仓手续费为5元/手
              SetTradeFee('T', 0, 5) 设置平今手续费为5元/手
        '''
        return self._dataModel.setTradeFee(type, rateFee, fixFee)

    def SetTradeMode(self, inActual, sendOrderType, useSample, useReal):
        '''
        【说明】
             设置运行方式，"H"表示回测，"A"表示在实盘上运行

        【语法】
              int SetTradeMode(inActual, sendOrderType, useSample, useReal)

        【参数】
              inActual True 表示在实盘上运行，False 表示在模拟盘上运行
              sendOrderType 在实盘上的发单方式，1 表示实时发单,2 表示K线完成后发单
              useSample     在模拟盘上是否使用历史数据进行回测
              useReal       在模拟盘上是否使用实时数据运行策略

        【备注】
              返回整型，0成功，-1失败

        【示例】
              SetTradeMode(False, 0, True, True)    # 在模拟盘上使用历史数据回测，并使用实时数据继续运行策略
              SetTradeMode(True, 2, True, True)     # 在模拟盘上使用历史数据回测，并使用实时数据继续运行策略；在实盘上使用实时数据运行策略，并在K线稳定后发单
        '''
        return self._dataModel.setTradeMode(inActual, sendOrderType, useSample, useReal)


baseApi = BaseApi()

#////////////////////全局函数定义//////////////
#K线函数
def Date():
    return baseApi.Date()

def D():
    return baseApi.Date()

def Time():
    return baseApi.Time()

def T():
    return baseApi.Time()

def Open(symbol=''):
    return baseApi.Open(symbol)

def O(symbol=''):
    return baseApi.Open(symbol)

def High(symbol=''):
    return baseApi.High(symbol)

def H(symbol=''):
    return baseApi.High(symbol)

def Low(symbol=''):
    return baseApi.Low(symbol)

def L(symbol=''):
    return baseApi.Low(symbol)

def Close(symbol=''):
    return baseApi.Close(symbol)

def C(symbol=''):
    return baseApi.Close(symbol)

def Vol(symbol=''):
    return baseApi.Vol(symbol)

def V(symbol=''):
    return baseApi.Vol(symbol)

def OpenInt(symbol=''):
    return baseApi.OpenInt(symbol)

def TradeDate():
    return baseApi.TradeDate()

def BarCount():
    return baseApi.BarCount()

def CurrentBar():
    return baseApi.CurrentBar()

def BarStatus():
    return baseApi.BarStatus()

def HistoryDataExist():
    return baseApi.HistoryDataExist()

#即时行情
def Q_AskPrice(symbol='', level=1):
    return baseApi.Q_AskPrice(symbol, level)

def Q_AskPriceFlag(symbol=''):
    return baseApi.Q_AskPriceFlag(symbol)

def Q_AskVol(symbol='', level=1):
    return baseApi.Q_AskVol(symbol, level)

def Q_AvgPrice(symbol=''):
    return baseApi.Q_AvgPrice(symbol)

def Q_BidPrice(symbol='', level=1):
    return baseApi.Q_BidPrice(symbol, level)

def Q_BidPriceFlag(symbol=''):
    return baseApi.Q_BidPriceFlag(symbol)

def Q_BidVol(symbol='', level=1):
    return baseApi.Q_BidVol(symbol, level)

def Q_Close(symbol=''):
    return baseApi.Q_Close(symbol)

def Q_High(symbol=''):
    return baseApi.Q_High(symbol)

def Q_HisHigh(symbol=''):
    return baseApi.Q_HisHigh(symbol)

def Q_HisLow(symbol=''):
    return baseApi.Q_HisLow(symbol)

def Q_InsideVol(symbol=''):
    return baseApi.Q_InsideVol(symbol)

def Q_Last(symbol=''):
    return baseApi.Q_Last(symbol)

def Q_LastDate(symbol=''):
    return baseApi.Q_LastDate(symbol)

def Q_LastFlag(symbol=''):
    return baseApi.Q_LastFlag(symbol)

def Q_LastTime(symbol=''):
    return baseApi.Q_LastTime(symbol)

def Q_LastVol(symbol=''):
    return baseApi.Q_LastVol(symbol)

def Q_Low(symbol=''):
    return baseApi.Q_Low(symbol)

def Q_LowLimit(symbol=''):
    return baseApi.Q_LowLimit(symbol)

def Q_Open(symbol=''):
    return baseApi.Q_Open(symbol)

def Q_OpenInt(symbol=''):
    return baseApi.Q_OpenInt(symbol)

def Q_OpenIntFlag(symbol=''):
    return baseApi.Q_OpenIntFlag(symbol)

def Q_OutsideVol(symbol=''):
    return baseApi.Q_OutsideVol(symbol)

def Q_PreOpenInt(symbol=''):
    return baseApi.Q_PreOpenInt(symbol)

def Q_PreSettlePrice(symbol=''):
    return baseApi.Q_PreSettlePrice(symbol)

def Q_PriceChg(symbol=''):
    return baseApi.Q_PriceChg(symbol)

def Q_PriceChgRadio(symbol=''):
    return baseApi.Q_PriceChgRadio(symbol)

def Q_TodayEntryVol(symbol=''):
    return baseApi.Q_TodayEntryVol(symbol)

def Q_TodayExitVol(symbol=''):
    return baseApi.Q_TodayExitVol(symbol)

def Q_TotalVol(symbol=''):
    return baseApi.Q_TotalVol(symbol)

def Q_TurnOver(symbol=''):
    return baseApi.Q_TurnOver(symbol)

def Q_UpperLimit(symbol=''):
    return baseApi.Q_UpperLimit(symbol)

def QuoteDataExist(symbol=''):
    return baseApi.QuoteDataExist(symbol)

#账户函数
def A_AccountID():
    return baseApi.A_AccountID()

def A_Cost():
    return baseApi.A_Cost()

def A_CurrentEquity():
    return baseApi.A_CurrentEquity()

def A_FreeMargin():
    return baseApi.A_FreeMargin()

def A_ProfitLoss():
    return baseApi.A_ProfitLoss()

def A_TotalFreeze():
    return baseApi.A_TotalFreeze()

def A_BuyAvgPrice(contNo=''):
    return baseApi.A_BuyAvgPrice(contNo)

def A_BuyPosition(contNo=''):
    return baseApi.A_BuyPosition(contNo)

def A_BuyProfitLoss(contNo=''):
    return baseApi.A_BuyProfitLoss(contNo)

def A_SellAvgPrice(contNo=''):
    return baseApi.A_SellAvgPrice(contNo)

def A_SellPosition(contNo=''):
    return baseApi.A_SellPosition(contNo)

def A_SellProfitLoss(contNo=''):
    return baseApi.A_SellProfitLoss(contNo)

def A_TotalAvgPrice(contNo=''):
    return baseApi.A_TotalAvgPrice(contNo)

def A_TotalPosition(contNo=''):
    return baseApi.A_TotalPosition(contNo)

def A_TotalProfitLoss(contNo=''):
    return baseApi.A_TotalProfitLoss(contNo)

def A_TodayBuyPosition(contNo=''):
    return baseApi.A_TodayBuyPosition(contNo)

def A_TodaySellPosition(contNo=''):
    return baseApi.A_TodaySellPosition(contNo)

def A_OrderBuyOrSell(eSession=''):
    return baseApi.A_OrderBuyOrSell(eSession)

def A_OrderEntryOrExit(eSession=''):
    return baseApi.A_OrderEntryOrExit(eSession)

def A_OrderFilledLot(eSession=''):
    return baseApi.A_OrderFilledLot(eSession)

def A_OrderFilledPrice(eSession=''):
    return baseApi.A_OrderFilledPrice(eSession)

def A_OrderLot(eSession=''):
    return baseApi.A_OrderLot(eSession)

def A_OrderPrice(eSession=''):
    return baseApi.A_OrderPrice(eSession)

def A_OrderStatus(eSession=''):
    return baseApi.A_OrderStatus(eSession)

def A_OrderTime(eSession=''):
    return baseApi.A_OrderTime(eSession)

def A_SendOrder(userNo, contNo, orderType, validType, orderDirct, entryOrExit, hedge, orderPrice, orderQty):
    return baseApi.A_SendOrder(userNo, contNo, orderType, validType, orderDirct, entryOrExit, hedge, orderPrice, orderQty)

def A_DeleteOrder(eSession):
    return baseApi.A_DeleteOrder(eSession)

#策略交易
def Buy(share=0, price=0):
    return baseApi.Buy(share, price)

def BuyToCover(share=0, price=0):
    return baseApi.BuyToCover(share, price)

def Sell(share=0, price=0):
    return baseApi.Sell(share, price)

def SellShort(share=0, price=0):
    return baseApi.SellShort(share, price)
    
#绘图函数
def PlotNumeric(name, value, locator=0, color=0xdd0000, barsback=0):
    return baseApi.PlotNumeric(name, value, locator, color, barsback)
    
#枚举函数
def Enum_Period_Tick():
    return baseApi.Enum_Period_Tick()
    
def Enum_Period_Dyna(): 
    return baseApi.Enum_Period_Dyna()
    
def Enum_Period_Second():
    return baseApi.Enum_Period_Second()
    
def Enum_Period_Min():
    return baseApi.Enum_Period_Min()
    
def Enum_Period_Hour():
    return baseApi.Enum_Period_Hour()
    
def Enum_Period_Day():
    return baseApi.Enum_Period_Day()
    
def Enum_Period_Week():
    return baseApi.Enum_Period_Week()
    
def Enum_Period_Month():
    return baseApi.Enum_Period_Month()
    
def Enum_Period_Year():
    return baseApi.Enum_Period_Year()
    
def Enum_Period_DayX():
    return baseApi.Enum_Period_DayX()


# 设置函数
def GetConfig():
    return baseApi.GetConfig()

def SetBenchmark(symbolTuple):
    return baseApi.SetBenchmark(symbolTuple)

def SetUserNo(userNo=''):
    return baseApi.SetUserNo(userNo)

def SetBarInterval(barType, barInterval):
    return baseApi.SetBarInterval(barType, barInterval)

def SetAllKTrue():
    return baseApi.SetAllKTrue()

# def SetBarPeriod(beginDate, endDate=0):
#     return baseApi.SetBarPeriod(beginDate, endDate)
def SetBarPeriod(beginDate):
    return baseApi.SetBarPeriod(beginDate)
    
def SetBarCount(count):
    return baseApi.SetBarCount(count)

def SetInitCapital(capital=''):
    return baseApi.SetInitCapital(capital)

def SetMargin(type, value=0):
    return baseApi.SetMargin(type, value)

def SetTradeFee(type, reteFee, fixFee):
    return baseApi.SetTradeFee(type, reteFee, fixFee)

def SetTradeMode(inActual, sendOrderType, useSample, useReal):
    return baseApi.SetTradeMode(inActual, sendOrderType, useSample, useReal)


# 属性函数
def BarInterval():
    return baseApi.BarInterval()

def BarType():
    return baseApi.BarType()

def BidAskSize(contNo=''):
    return baseApi.BidAskSize(contNo)

def BigPointValue(contNo=''):
    return baseApi.BigPointValue(contNo)

def CanTrade(contNo=''):
    return baseApi.CanTrade(contNo)

def ContractUnit(contNo=''):
    return baseApi.ContractUnit(contNo)

def ExchangeName(contNo=''):
    return baseApi.ExchangeName(contNo)

def ExpiredDate(contNo=''):
    return baseApi.ExpiredDate(contNo)

def GetSessionCount(contNo=''):
    return baseApi.GetSessionCount(contNo)

def GetSessionEndTime(contNo='', index=0):
    return baseApi.GetSessionEndTime(contNo, index)

def GetSessionStartTime(contNo='', index=0):
    return baseApi.GetSessionStartTime(contNo, index)

def MarginRatio(contNo=''):
    return baseApi.MarginRatio(contNo)

def MaxBarsBack():
    return baseApi.MaxBarsBack()

def MaxSingleTradeSize():
    return baseApi.MaxSingleTradeSize()

def MinMove(contNo=''):
    return baseApi.MinMove(contNo)

def OptionStyle(contNo=''):
    return baseApi.OptionStyle(contNo)

def OptionType(contNo=''):
    return baseApi.OptionType(contNo)

def PriceScale(contNo=''):
    return baseApi.PriceScale(contNo)

def RelativeSymbol():
    return baseApi.RelativeSymbol()

def StrikePrice():
    return baseApi.StrikePrice()

def Symbol():
    return baseApi.Symbol()

def SymbolName(contNo=''):
    return baseApi.SymbolName(contNo)

def SymbolType(contNo=''):
    return baseApi.SymbolType(contNo)

