import sys
import os
import time
import sqlite3
import tushare as ts
from structured_fund import data, window
from PyQt5 import QtWidgets, QtCore
from multiprocessing import Process, Queue


structure_fund_mother = {}
structure_fund_a = {}
structure_fund_b = {}


class StructuredFund(object):

    def format_data(self):
        # The variables are transformed to strings for display
        code = self.a_code
        name = self.a_name
        price = str('{0:.3f}'.format(self.a_price))
        increase_percentage = str('{0:.2f}'.format(self.a_increase_percentage * 100)) + '%'
        amount = str('{0:.1f}'.format(self.a_amount / 10000)) + '万'
        bid = str('{0:.3f}'.format(self.a_bid))
        b1_v = str(self.a_b1_v)
        ask = str('{0:.3f}'.format(self.a_ask))
        a1_v = str(self.a_a1_v)
        high = str('{0:.3f}'.format(self.a_high))
        low = str('{0:.3f}'.format(self.a_low))
        pre_close = str('{0:.3f}'.format(self.a_pre_close))
        today_open = str('{0:.3f}'.format(self.a_today_open))
        timestamp = self.a_timestamp
        premium_rate = str('{0:.2f}'.format(self.a_premium_rate * 100)) + '%'
        net_value = str('{0:.3f}'.format(self.a_net_value))
#        annual_yield = str('{0:.3f}'.format(self.annual_yield * 100)) + '%'

        return code, name, price, increase_percentage, net_value, premium_rate, amount, bid, b1_v, ask, a1_v, \
            high, low, pre_close, today_open


def update_realtime_quotations(queue):
    structured_fund = data.StructuredFund()
    structured_fund.init_fund_info()
    structured_fund.init_fund_code()
    while True:
        new_date = structured_fund.update_realtime_quotations()
        if new_date:
            queue.put(structured_fund.output_a())
        time.sleep(1)


def emit_data(structured_fund_window, queue):
    if queue.empty() is False:
        data_table = queue.get(True)
        structured_fund_window.signal_fill_table.emit(data_table)
        structured_fund_window.signal_statusbar_showmessage.emit('数据更新正常，当前时间：{0}，数据时间：1'.format(
           time.strftime('%H:%M:%S', time.localtime()) ))#timestamp))


def window_show(queue):
    app = QtWidgets.QApplication(sys.argv)
    structured_fund_window = window.MyWindow()
    structured_fund_window.show()
    structured_fund_window.timer = QtCore.QTimer()
    structured_fund_window.timer.timeout.connect(lambda: emit_data(structured_fund_window, queue))
    structured_fund_window.timer.start(100)
    sys.exit(app.exec_())


if __name__ == '__main__':
    q = Queue()
    process_data = Process(target=update_realtime_quotations, args=(q,))
    process_window = Process(target=window_show, args=(q,))
    process_data.start()
    process_window.start()
    process_data.join()
    process_data.terminate()

