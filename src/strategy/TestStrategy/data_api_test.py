"""本策略用于测试数据函数BarCount, BarStatus, CurrentBar, Date, D, High, H, Open, O, Low, L, Close, C, Time, T"""

from starapi.api import *


def initialize(context):
    # AddTimes(3)
    # Trade_Other('SHFE|F|RB|1905')
    # print("initialize")
    context.i = 0

def handle_data(context):
    # BarsLast(a, H>C)
    # BarsLast(L > C)
    bar_count = BarCount()
    bar_status = BarStatus()
    current_bar = CurrentBar()
    # data.Close()
    date = Date()
    d = D()
    high = High()
    h = H()
    open = Open()
    o = O()
    low = Low()
    l = L()
    close = Close()
    c = C()
    time = Time()
    t = T()

    context.i = context.i + 1
    print("handle_data: ", context.i)
    print('所有bar上的数据:')
    print('BarCount: {} \nBarStatus: {} \nCurrentBar: {} \nDate: {} \nD: {} \nHigh: {} \nH: {} \n'
          'Open: {} \nO: {} \nLow: {} \nL: {} \nClose: {} \nC: {} \nTime: {}\nT: {}'.format(
        bar_count, bar_status, current_bar, date, d, high, h, open, o, low, l, close, c, time, t))
        # print('当前bar上的数据')
        # print('BarCount: {} \nBarStatus: {} \nCurrentBar: {} \nDate: {} \nD: {} \nHigh: {} \nH: {} \n'
        #       'Open: {} \nO: {} \nLow: {} \nL: {} \nClose: {} \nC: {} \nTime: {}\nT: {}'.format(
        #     bar_count[-1], bar_status[-1], current_bar[-1], date[-1], d[-1], high[-1], h[-1], open[-1], o[-1], low[-1],
        #     l[-1], close[-1], c[-1], time[-1], t[-1]))
