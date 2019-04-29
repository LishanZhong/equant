"""本策略用于测试其他函数PlotNumic"""
from starapi.api import *


def initialize(context):
    print("initialize")
    context.i = 0


def handle_data(context):
    PlotNumic('High', High()[-1])
    PlotNumic('Open', Open()[-1])
    PlotNumic('Low', Low()[-1])
    PlotNumic('Close', Close()[-1])
    print(Close()[-1])

    context.i = context.i + 1
    print("handle_data: ", context.i)
