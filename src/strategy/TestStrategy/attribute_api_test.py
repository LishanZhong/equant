"""本策略用于测试属性函数"""
#from starapi.api import *


def initialize(context):
    pass
    #context.i = 0
    # self.AddAccount('Q1351868270')
    # SetBenchmarkContract('NYMEX|Z|CL|MAIN')
    # SetBenchmarkAccount('Q1351868270')
    # Trade_Other('NYMEX|F|CL|1905')


def handle_data(context):
    print("================ 属性函数 ================")
    barInterval = BarInterval()
    # print("图表周期数值 : ", barInterval)
    barType = BarType()
    print("图标周期类型 : ", barType)
    bidAskSize = BidAskSize()
    print("买卖盘个数 : ", bidAskSize)
    bigPointValue = BigPointValue("HKEX|F|A50|888")
    print("每点价值 : ", bigPointValue)
    # canTrade = CanTrade()
    # print("是否支持交易 : ", canTrade)
    contUnit = ContractUnit()
    print("每手乘数 : ", contUnit)
    exchangeName = ExchangeName()
    print("交易所名称 : ", exchangeName)
    
    sessionCount = GetSessionCount("APEX|F|FO|888")
    print("交易时段个数 : ", sessionCount)
    sessionEndTime = GetSessionEndTime("ZCE|F|SR|905", 3)
    print("交易时段结束时间 : ", sessionEndTime)
    sessionStartTime = GetSessionStartTime("ZCE|F|SR|905", 3)
    print("交易时段起始时间 : ", sessionStartTime)
    
    marginRatio = MarginRatio()
    print("保证金比例 : ", marginRatio)
    maxBarsBack = MaxBarsBack()
    print("最大回溯Bar数 : ", maxBarsBack)
    maxSingleTradeSize = MaxSingleTradeSize()
    print("单笔交易限量 : ", maxSingleTradeSize)
    minMove = MinMove()
    print("最小变动量 : ", minMove)
    
    optStyle = OptionStyle()
    print("期权类型 : ", optStyle)
    optType = OptionType()
    print("看涨看跌 : ", optType)
    priceScale = PriceScale()
    print("价格精度 : ", priceScale)
    relativeSymbol = RelativeSymbol()
    print("关联合约 : ", relativeSymbol)
    strikePrice = StrikePrice()
    print("期权行权价 : ", strikePrice)
    symbol = Symbol()
    print("合约编号 : ", symbol)
    symbolName = SymbolName("APEX|F|CPF|1905")
    print("合约名称 : ", symbolName)
    symbolType = SymbolType()
    print("品种编号 : ", symbolType)
    
    '''
    bar_interval = BarInterval()
    bar_type = BarType()
    bid_ask_size = BidAskSize()
    big_point_value = BigPointValue()
    can_market_order = CanMarketOrder()
    can_trade = CanTrade()
    contract_unit = ContractUnit()
    exchange_name = ExchangeName()
    #
    # get_session_count = GetSessionCount()
    # for i in range(GetSessionCount()):
    #     get_session_end_time = GetSessionEndTime(i)
    #     get_session_start_time = GetSessionStartTime(i)
    #
    min_move = MinMove()
    # option_style = OptionStyle()
    option_type = OptionType()
    price_scale = PriceScale()
    symbol = Symbol()
    symbol_name = SymbolName()
    symbol_type = SymbolType()
    context.i = context.i + 1
    print("handle_data: ", context.i)
    print('BarInterval: {} \nBarType: {} \nBidAskSize: {} \nBigPointValue: {} \nCanMarketOrder: {} \nCanTrade: {} \nContractUnit: {} \n'
          'ExchangeName: {} \nMinMove: {} \nOptionType: {} \nPriceScale: {} \nSymbol: {} \nSymbolName: {}\nSymbolType: {}'.format(
        bar_interval, bar_type, bid_ask_size, big_point_value, can_market_order, can_trade, contract_unit,
        exchange_name, min_move, option_type, price_scale, symbol, symbol_name, symbol_type))
    pass
    '''



