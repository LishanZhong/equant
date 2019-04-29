import os
import pickle
import time
from datetime import datetime

from capi.com_types import *


def rgb_to_hex(r, g, b):
    output = "#"
    tmp = (r, g, b)
    for x in tmp:
        if x < 16:
            output = output + "0" + hex(x)[2:]
        else:
            output = output + hex(x)[2:]
    return output


def load_file(path):
    with open(path, "r", encoding="utf-8") as f:
        data = f.read()
    return data


def int2date(d):
    millisecond = d%1000
    second = int(d/1000)%100
    minute = int(d/100000)%100
    hour = int(d/10000000)%100
    day = int(d/1000000000)%100
    month = int(d/100000000000)%100
    year = int(d/10000000000000)
    time = '{:0>4d}-{:0>2d}-{:0>2d} {:0>2d}:{:0>2d}:{:0>2d}.{:0>3d}'.format(year, month, day, hour, minute, second, millisecond)
    return time


def save(data):
    # 保存回测运行数据

    # runType = get_execute_type()
    runType = "测试"
    strategyName = "双均线交易系统"
    file_path = os.path.abspath(r"./reportdata/")
    current_time = time.strftime('%Y-%m-%d %H.%M.%S', time.localtime(time.time()))
    file_name = file_path + '\\' + strategyName + '\\' + runType + current_time + '.pkl'
    strategyPath = file_path + '\\' + strategyName

    if not os.path.exists(strategyPath):
        os.mkdir(strategyPath)
        with open(file_name, 'wb') as f:
            pickle.dump(data, f)

    else:
        with open(file_name, 'wb') as f:
            pickle.dump(data, f)


def get_execute_type(strategy):
    #TODO: 执行类型先写一个定值吧
    if strategy.config.execute_type == EEQU_TRADE_TYPE_H:
        return "测试"

    if strategy.config.execute_type == EEQU_TRADE_TYPE_A:
        return "实盘"

def parseYMD(date):
    """
    将日期（2011/11/11）转换为指定格式
    :param date: 日期
    :return: 时间组成的字符串：'20110203'
    """
    year_, mon_, day_ = date.split("/")
    tempDate = datetime(int(year_), int(mon_), int(day_))
    return datetime.strftime(tempDate, '%Y%m%d')

def parseTime(time):
    """
    将时刻转换为指定格式
    :param time: 时刻格式：hhmmss
    :return: 时间组成的字符串：’yyyymmddhhmmss'
    """
    now_ = datetime.now()
    tempTime = datetime.strftime(now_, '%Y%m%d')
    return tempTime + time

