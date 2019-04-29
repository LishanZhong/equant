#-----------------弃用-----------------------
"""
回测结果所需数据
"""
import collections


class Result(object):
    """获取回测结果数据"""
    def __init__(self, dataModel):
        self._dataModel = dataModel
        self._reportDetails = self._dataModel.getReportDetail()
        self._order = self._dataModel.getOrders
        self._stageResult = self._setStageRlt()
        self._fundRecord = self._dataModel.getFundRecord()
        self._KLineType = self._dataModel.getKLineType()

    def _setStageRlt(self):
        stageResult = collections.OrderedDict()
        stageResult.update({
            "年度分析": self._dataModel.getYearStatis,
            "季度分析": self._dataModel.getQuarterStatis,
            "月度分析": self._dataModel.getMonthStatis,
            "周分析": self._dataModel.getWeekStatis,
            "日分析": self._dataModel.getDailyStatis
        })
        return stageResult

    def result(self):
        return {
            'Fund': self._fundRecord,
            'Detail': self._reportDetails,
            'Stage': self._stageResult,
            'Orders': self._order,
            'KLineType': self._KLineType
        }