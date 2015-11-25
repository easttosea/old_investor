# -*- coding: utf-8 -*-
from structured_fund.ui import Ui_Form
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QColor


class MyWindow(QtWidgets.QMainWindow, Ui_Form):
    signal_fill_table = QtCore.pyqtSignal(list, list)
    signal_statusbar_showmessage = QtCore.pyqtSignal(str)

    def __init__(self):
        super(MyWindow, self).__init__()
        self.setupUi(self)
        self.tableWidget_list.setHorizontalHeaderLabels(
            ['代码', '名称', '现价',  '涨幅', '成交额', '净值', '溢价率', '利率规则', '本期利率', '下期利率',
             '修正收益率'])
        self.statusBar().showMessage('准备开始')
        self.signal_fill_table.connect(self.fill_the_table)
        self.signal_statusbar_showmessage.connect(self.statusBar().showMessage)

    def fill_the_table(self, fund_a, a_volume_0):
        row = 0
        for fund in fund_a:
            a_code = QtWidgets.QTableWidgetItem(fund[0])
            a_name = QtWidgets.QTableWidgetItem(fund[1])
            a_price = QtWidgets.QTableWidgetItem(fund[2])
            a_increase_rate = QtWidgets.QTableWidgetItem(fund[3])
            a_increase_value = fund[4]
            a_amount = QtWidgets.QTableWidgetItem(fund[5])
            a_net_value = QtWidgets.QTableWidgetItem(fund[6])
            a_premium_rate = QtWidgets.QTableWidgetItem(fund[7])
            rate_rule = QtWidgets.QTableWidgetItem(fund[8])
            current_annual_rate = QtWidgets.QTableWidgetItem(fund[9])
            next_annual_rate = QtWidgets.QTableWidgetItem(fund[10])
            modified_rate_of_return = QtWidgets.QTableWidgetItem(fund[11])
            if a_increase_value > 0:
                a_price.setForeground(QtCore.Qt.red)
                a_increase_rate.setForeground(QtCore.Qt.red)
            elif a_increase_value < 0:
                a_price.setForeground(QtCore.Qt.darkGreen)
                a_increase_rate.setForeground(QtCore.Qt.darkGreen)
            if fund[0] in a_volume_0:
                a_code.setForeground(QtCore.Qt.gray)
                a_name.setForeground(QtCore.Qt.gray)
                a_price.setForeground(QtCore.Qt.gray)
                a_increase_rate.setForeground(QtCore.Qt.gray)
                a_amount.setForeground(QtCore.Qt.gray)
                a_net_value.setForeground(QtCore.Qt.gray)
                a_premium_rate.setForeground(QtCore.Qt.gray)
                rate_rule.setForeground(QtCore.Qt.gray)
                current_annual_rate.setForeground(QtCore.Qt.gray)
                next_annual_rate.setForeground(QtCore.Qt.gray)
                modified_rate_of_return.setForeground(QtCore.Qt.gray)
            self.tableWidget_list.setItem(row, 0, a_code)
            self.tableWidget_list.setItem(row, 1, a_name)
            self.tableWidget_list.setItem(row, 2, a_price)
            self.tableWidget_list.setItem(row, 3, a_increase_rate)
            self.tableWidget_list.setItem(row, 4, a_amount)
            self.tableWidget_list.setItem(row, 5, a_net_value)
            self.tableWidget_list.setItem(row, 6, a_premium_rate)
            self.tableWidget_list.setItem(row, 7, rate_rule)
            self.tableWidget_list.setItem(row, 8, current_annual_rate)
            self.tableWidget_list.setItem(row, 9, next_annual_rate)
            self.tableWidget_list.setItem(row, 10, modified_rate_of_return)
#            column = 0
#            for content in fund:
#                content_for_fill = QtWidgets.QTableWidgetItem(content)
#                self.tableWidget_list.setItem(row, column, content_for_fill)
#                column += 1
            row += 1
#        self.tableWidget_list.resizeColumnsToContents()
