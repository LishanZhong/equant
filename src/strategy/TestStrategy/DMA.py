#-*-coding:utf-8
import talib

def initialize(context):
    SetBenchmark(("NYMEX|F|CL|1906",))
    SetBarInterval('M',1)
    SetBarPeriod("20190429")


def handle_data(context):
    ma1 = talib.MA(Close(), timeperiod=5)
    ma2 = talib.MA(Close(), timeperiod=20)
    
    #记录指标
    PlotNumeric('MA1', ma1[-1])
    PlotNumeric('MA2', ma2[-1], color=0x00aa00)
    
    
    if len(ma1) <= 5 or len(ma2) <= 20:
        return
    
    if ma1[-1] > ma2[-1]:
        Buy(1, Open()[-1])               # 买平开
    if ma1[-1] < ma2[-1]:
        SellShort(1, Open()[-1])         # 卖平开

























































