"""本策略用于测试账户函数A_SendOrder"""

from starapi.api import *
import time


def initialize(context):
    pass
    # self.AddAccount('Q1351868270')
    # SetBenchmarkContract('NYMEX|Z|CL|MAIN')
    # SetBenchmarkAccount('Q1351868270')
    # Trade_Other('NYMEX|F|CL|1905')


def handle_data(context):
    print("================ 账户函数 ================")
    account = A_AccountID()
    print("交易账户ID : ", account)
    cost = A_Cost()
    print("手续费 : ", cost)
    currentEquity = A_CurrentEquity()
    print("账户权益 : ", currentEquity)
    freeMargin = A_FreeMargin()
    print("可用资金 : ", freeMargin)
    profitLoss = A_ProfitLoss()
    print("浮动盈亏 : ", profitLoss)
    totalFreeze = A_TotalFreeze()
    print("冻结资金 : ", totalFreeze)  
    
    buyAvgPrice = A_BuyAvgPrice()
    print("买入均价 : ", buyAvgPrice)
    buyPosition = A_BuyPosition("ZCE|F|CF|905")
    print("买持仓量 : ", buyPosition)
    buyProfitLoss = A_BuyProfitLoss()
    print("买浮动盈亏 : ", buyProfitLoss)
    
    sellAvgPrice = A_SellAvgPrice("ZCE|F|CF|905")
    print("卖出均价 : ", sellAvgPrice)
    sellPosition = A_SellPosition("ZCE|F|CF|905")
    print("卖出持仓", sellPosition)
    sellProfitLoss = A_SellProfitLoss()
    print("卖浮动盈亏 : ", sellProfitLoss)
    totalAvgPrice = A_TotalAvgPrice("ZCE|F|CF|905")
    print("总持仓均价 : ", totalAvgPrice)
    totalPosition = A_TotalPosition()
    print("总持仓量 : ", totalPosition)
    totalPositionLoss = A_TotalProfitLoss()
    print("总浮动盈亏 : ", totalPositionLoss)
    todayBuyPosition = A_TodayBuyPosition()
    print("当日买持仓 : ", todayBuyPosition)
    todaySellPosition = A_TodaySellPosition("ZCE|F|CF|905")
    print("当日卖持仓 : ", todaySellPosition)
    
    sessionId = A_SendOrder("15838089576", "ZCE|F|SR|905", '2', '0', 'B', 'O', 'T', 5168, 1)
    print("下单 : ", sessionId)
    
    time.sleep(10)
    
    orderBuyOrSell = A_OrderBuyOrSell(sessionId)
    print("买卖方向 : ", orderBuyOrSell)
    orderEntryOrExit = A_OrderEntryOrExit()
    print("开平标识 : ", orderEntryOrExit)
    orderFilledLot = A_OrderFilledLot(sessionId)
    print("定单成交数量 : ", orderFilledLot)
    orderFilledPrice = A_OrderFilledPrice()
    print("定单成交价格 : ", orderFilledPrice)
    orderLot = A_OrderLot(sessionId)
    print("委托数量 : ", orderLot)
    orderPrice = A_OrderPrice(sessionId)
    print("委托价格 : ", orderPrice)
    orderStatus = A_OrderStatus(sessionId)
    print("定单状态 : ", orderStatus)
    orderTime = A_OrderTime(sessionId)
    print("下单时间 : ", orderTime)
    
    deleteOrder = A_DeleteOrder(sessionId)
    print("撤单 : ", deleteOrder)
    
    # modifyOrder = A_ModifyOrder(sessionId, "ZCE|F|SR|905", 'B', 'O', 5265, 3)
    
    '''
    if BarStatus()[-1] == 2:
        orderid = A_SendOrder(Enum_Buy(), Enum_Entry(), 1, Close()[-1])
        delete_order = A_DeleteOrder(orderid)
        account = A_AccountID()
        print("交易账户ID : ", account)
        free_margin = A_FreeMargin()
        profitloss = A_ProfitLoss()
        BuyAvgPrice = A_BuyAvgPrice()
        BuyPosition = A_BuyPosition()
        buyorsell = A_OrderBuyOrSell(orderid)
        entryorexit = A_OrderEntryOrExit(orderid)
        FilledLot = A_OrderFilledLot(orderid)
        FilledPrice = A_OrderFilledPrice(orderid)
        Lot = A_OrderLot(orderid)
        Price = A_OrderPrice(orderid)
        Status = A_OrderStatus(orderid)
        time = A_OrderTime(orderid)
        print('orderid: ', orderid)

    context.i = context.i + 1
    print("handle_data: ", context.i)
    '''












































































