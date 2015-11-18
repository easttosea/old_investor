# -*- coding: utf-8 -*-
from structured_fund.ui import Ui_Form_structured_fund
from PyQt5 import QtWidgets, QtCore


class MyWindow(QtWidgets.QMainWindow, Ui_Form_structured_fund):
    signal_fill_table = QtCore.pyqtSignal(list, dict)
    signal_statusbar_showmessage = QtCore.pyqtSignal(str)

    def __init__(self):
        super(MyWindow, self).__init__()
        self.setupUi(self)
        self.statusBar().showMessage('准备开始')
        self.signal_fill_table.connect(self.fill_the_table)
        self.signal_statusbar_showmessage.connect(self.statusBar().showMessage)

    def fill_the_table(self, fund_code_list, fund_a):
        row = 0
        for fund_code in fund_code_list:
            fund = fund_a[fund_code].format_data()
            column = 0
            for content in fund:
                content_for_fill = QtWidgets.QTableWidgetItem(content)
                self.tableWidget_structured_fund.setItem(row, column, content_for_fill)
                column += 1
            row += 1
        self.tableWidget_structured_fund.resizeColumnsToContents()