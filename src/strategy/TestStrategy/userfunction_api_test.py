from starapi.userlib import UserLib
from starapi.api.userfunction_api import BarLast

class UserStrategy(UserLib):
    def initialize(self):
        self.i = 0
        # self.AddAccount('Q1351868270')
        self.SetBenchmarkContract('NYMEX|Z|CL|MAIN')
        self.SetBenchmarkAccount('Q1351868270')
        self.Trade_Other('NYMEX|F|CL|1905')
        self._BarLast1 = BarLast(self)
        self._BarLast2 = BarLast(self)
        self._BarLast3 = BarLast(self)

    def handle_data(self):
        a = self._BarLast1(self.Close[-1] > self.Open[-1])
        b = self._BarLast2(self.Close[-1] > 20)
        c = self._BarLast3(self.Close[-1] > 100)
        orderid = self.A_SendOrder(self.Enum_Buy, self.Enum_Entry, 1, self.Close[-1])
        print(self.A_DeleteOrder(orderid))