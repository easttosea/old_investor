import sys
import os
import time
import sqlite3
import tushare as ts
from structured_fund import data, gui
from PyQt5 import QtWidgets, QtCore
from multiprocessing import Process, Queue


def update_realtime_quotations(queue):
    structured_fund = data.StructuredFund()
    structured_fund.init_fund_info()
    structured_fund.init_fund_code()
    while True:
        new_data = structured_fund.update_realtime_quotations()
        if new_data:
            queue.put(structured_fund.frame_realtime)
        time.sleep(1)


def emit_data(structured_fund_gui, queue):
    if queue.empty() is False:
        structured_fund_gui.frame_realtime = queue.get(True)
        structured_fund_gui.signal_fill_table_list.emit()
        structured_fund_gui.signal_fill_table_handicap.emit()
    if structured_fund_gui.frame_realtime is None:
        structured_fund_gui.signal_statusbar_showmessage.emit('数据正在初始化，当前时间：{0}'.format(
            time.strftime('%H:%M:%S', time.localtime())))
    else:
        structured_fund_gui.signal_statusbar_showmessage.emit('数据更新正常，当前时间：{0}，数据时间：{1}'.format(
            time.strftime('%H:%M:%S', time.localtime()), structured_fund_gui.frame_realtime.a_time[0]))


def window_show(queue):
    app = QtWidgets.QApplication(sys.argv)
    structured_fund_gui = gui.MyWindow()
    structured_fund_gui.show()
    structured_fund_gui.timer = QtCore.QTimer()
    structured_fund_gui.timer.timeout.connect(lambda: emit_data(structured_fund_gui, queue))
    structured_fund_gui.timer.start(100)
    sys.exit(app.exec_())


if __name__ == '__main__':
    q = Queue()
    process_data = Process(target=update_realtime_quotations, args=(q,))
    process_window = Process(target=window_show, args=(q,))
    process_data.start()
    process_window.start()
    process_window.join()
    process_data.terminate()

