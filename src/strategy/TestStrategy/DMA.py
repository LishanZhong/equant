#-*-coding:utf-8
import talib

def initialize(context):
<<<<<<< HEAD
    SetBenchmark("NYMEX|F|CL|1906")
    SetBarInterval('M',1)
    SetBarPeriod("20190429")
    SetUserNo("ET001")
=======
    SetBenchmark(("NYMEX|F|CL|1906",))
    SetBarInterval('M',1)
    SetBarPeriod("20190429")
>>>>>>> ad1a21420c5a8681042ccd54b810f1d4c46d8e2e


def handle_data(context):
    ma1 = talib.MA(Close(), timeperiod=5)
    ma2 = talib.MA(Close(), timeperiod=20)
    
    #记录指标
    PlotNumeric('MA1', ma1[-1])
    PlotNumeric('MA2', ma2[-1], color=0x00aa00)
    
<<<<<<< HEAD
    if len(ma1) <= 5 or len(ma2) <= 20:
        return
        
=======
    
    if len(ma1) <= 5 or len(ma2) <= 20:
        return
    
>>>>>>> ad1a21420c5a8681042ccd54b810f1d4c46d8e2e
    if ma1[-1] > ma2[-1]:
        Buy(1, Open()[-1])               # 买平开
    if ma1[-1] < ma2[-1]:
        SellShort(1, Open()[-1])         # 卖平开

























































<<<<<<< HEAD










=======
>>>>>>> ad1a21420c5a8681042ccd54b810f1d4c46d8e2e
