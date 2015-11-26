import sys
import os
import time
import sqlite3
import tushare as ts
from structured_fund import data, window
from PyQt5 import QtWidgets, QtCore
from multiprocessing import Process, Queue


def update_realtime_quotations(queue):
    structured_fund = data.StructuredFund()
    structured_fund.init_fund_info()
    structured_fund.init_fund_code()
    while True:
        new_data = structured_fund.update_realtime_quotations()
        if new_data:
            queue.put([structured_fund.output_a(), structured_fund.a_volume_0])
        time.sleep(1)


def emit_data(structured_fund_window, queue):
    if queue.empty() is False:
        data_frame, a_volume_0 = queue.get(True)
        data_list = list(data_frame.loc[:, [
            'a_code', 'a_name', 'a_price', 'a_increase_rate', 'a_increase_value', 'a_amount',
            'a_net_value', 'a_premium_rate', 'rate_rule', 'current_annual_rate', 'next_annual_rate',
            'modified_rate_of_return']].values)
        structured_fund_window.signal_fill_table_list.emit(data_list, a_volume_0)
        data_handicap = list(data_frame.loc['168205', [
            'a_b1_p', 'a_b1_v', 'a_b2_p', 'a_b2_v', 'a_b3_p', 'a_b3_v', 'a_b4_p', 'a_b4_v', 'a_b5_p',
            'a_b5_v', 'a_a1_p', 'a_a1_v', 'a_a2_p', 'a_a2_v', 'a_a3_p', 'a_a3_v', 'a_a4_p', 'a_a4_v',
            'a_a5_p', 'a_a5_v', 'a_high', 'a_low', 'a_pre_close', 'a_open']].values)
        structured_fund_window.signal_fill_table_handicap.emit(data_handicap)
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

