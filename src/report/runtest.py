from report.reportview import ReportView
from report.datas import get_report_data
from report.utils import parse_new_data, save
from starapi.strategy import StrategyManager, ReportManager


def test_report_display(data):
    # strategy.other.cal.calc_last_static_info()
    report_data = data['Data']  # get_report_data(strategy)
    strategy = StrategyManager.retrieve(data['StrategyId'])
    save(strategy, data['Data'])
    if not ReportManager.report.children:  # 判断回测窗口的控件是否创建
        ReportView(report_data, ReportManager.report)
    else:
        # 显示最新回测结果
        ReportManager.report.children['!reportview'].children['!directory'].create_directory()
        ReportManager.report.children['!reportview'].children['!directory'].show(report_data)

    ReportManager.report.update()
    ReportManager.report.deiconify()


def history_report_display(window):
    # 直接点回测按钮打开历史回测窗口
    history_data = parse_new_data()
    import datetime
    #print(datetime.datetime.now().strftime("%H:%M:%S.%f"))
    ReportView(history_data, window)
    #print(datetime.datetime.now().strftime("%H:%M:%S.%f"))
    window.update()
    window.deiconify()
