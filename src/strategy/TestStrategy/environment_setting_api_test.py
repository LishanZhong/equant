#from starapi.api import *


def initialize(context):
    pass
    '''
    AddTimes(3)
    Trade_Other('SHFE|F|RB|1905')
    print("initialize")
    context.i = 0
    '''

def handle_data(context):
    print("================ 设置函数 ================")
    '''
    SetBenchmark("ZCE|F|SR|905", ['ZCE|F|AP|907', 'ZCE|F|AP|910'])
    SetBenchmark("ZCE|F|SR|912")
    print("config : ", GetConfig())

    print("config : ", GetConfig())
    SetBarInterval(0, 0)
    print("config : ", GetConfig())
    SetBarInterval(0, 1)
    print("config : ", GetConfig())
    SetBarInterval(0, 8)
    print("config : ", GetConfig())
    SetBarInterval(8, 8)
    print("config : ", GetConfig())
    SetBarInterval(9, 3)
    print("config : ", GetConfig())
    
    print("config : ", GetConfig())
    SetAllKTrue()
    print("config : ", GetConfig())
    SetBarPeriod('20190327')
    print("config : ", GetConfig())
    SetBarCount(666)
    print("config : ", GetConfig())
    
    print("config : ", GetConfig())
    SetInitCapital(300*10000)
    print("config : ", GetConfig())

    SetMargin(0)
    print("config : ", GetConfig()
    SetMargin(0, 0.1)
    print("config : ", GetConfig())
    SetMargin(1, 10000000)
    print("config : ", GetConfig())
    
    print("config : ", GetConfig())
    SetTradeFee('A', 0.1, 0)
    print("config : ", GetConfig())
    SetTradeFee('O', 0, 100000)
    print("config : ", GetConfig())
    SetTradeFee('T', 0.3, 0)
    print("config : ", GetConfig())
    SetTradeFee('C', 0.1, 2000000)
    print("config : ", GetConfig())
<<<<<<< HEAD
    
=======
    '''
>>>>>>> ad1a21420c5a8681042ccd54b810f1d4c46d8e2e
    print("config : ", GetConfig())
    SetTradeMode(False, 0, True, True)
    print("config : ", GetConfig())
    SetTradeMode(True, 2, True, True)
    print("config : ", GetConfig())
    SetTradeMode(False, 0, False, True)
    print("config : ", GetConfig())
<<<<<<< HEAD
    '''
    SetBenchmark("ZCE|F|SR|905", "ZCE|F|AP|907", "ZCE|F|AP|910")
    print("config : ", GetConfig())
=======


>>>>>>> ad1a21420c5a8681042ccd54b810f1d4c46d8e2e

    '''
    context.i = context.i + 1
    print("handle_data: ", context.i)
    '''















<<<<<<< HEAD





=======
>>>>>>> ad1a21420c5a8681042ccd54b810f1d4c46d8e2e
