from starapi.api import *


def initialize(context):
    AddTimes(3)
    Trade_Other('SHFE|F|RB|1905')
    print("initialize")
    context.i = 0


def handle_data(context):
    context.i = context.i + 1
    print('Buy: ')
    Buy(1, Open()[-1])  # 买平开
    print('Sell: ')
    Sell(1, Open()[-1])     # 卖平
    print('SellShort: ')
    SellShort(1, Open()[-1])  # 卖平开
    print('BuyToCover: ')
    BuyToCover(1, Open()[-1])  # 买平
    print("handle_data: ", context.i)
