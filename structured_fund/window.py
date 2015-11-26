# -*- coding: utf-8 -*-
from structured_fund.ui import Ui_Form
from PyQt5 import QtWidgets, QtCore
from PyQt5 import QtGui


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
        self.COLOR_RED = QtGui.QColor(200, 0, 0)
        self.COLOR_GREEN = QtGui.QColor(20, 150, 53)

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
            cell_list = [a_code, a_name, a_price, a_increase_rate, a_amount, a_net_value, a_premium_rate, rate_rule,
                         current_annual_rate, next_annual_rate, modified_rate_of_return]
            if fund[8] == '1年+3.0%':
                rate_rule.setForeground(QtGui.QColor(200, 0, 0))
            elif fund[8] == '1年+3.2%':
                rate_rule.setForeground(QtGui.QColor(200, 128, 0))
            elif fund[8] == '1年+3.5%' or fund[8] == '固定5.0%':
                rate_rule.setForeground(QtGui.QColor(200, 200, 0))
            elif fund[8] == '1年+4.0%' or fund[8] == '固定5.8%':
                rate_rule.setForeground(QtGui.QColor(128, 200, 0))
            elif fund[8] == '1年+4.5%' or fund[8] == '固定6.0%':
                rate_rule.setForeground(QtGui.QColor(0, 200, 0))
            elif fund[8] == '1年+5.0%':
                rate_rule.setForeground(QtGui.QColor(0, 200, 128))
            elif fund[8] == '固定7.0%':
                rate_rule.setForeground(QtGui.QColor(0, 200, 200))

            if a_increase_value > 0:
                a_price.setForeground(self.COLOR_RED)
                a_increase_rate.setForeground(self.COLOR_RED)
            elif a_increase_value < 0:
                a_price.setForeground(self.COLOR_GREEN)
                a_increase_rate.setForeground(self.COLOR_GREEN)

            if fund[0] in a_volume_0:
                for cell in cell_list:
                    cell.setForeground(QtGui.QColor(200, 200, 200))

            column = 0
            for cell in cell_list:
                cell.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
                self.tableWidget_list.setItem(row, column, cell)
                column += 1

#            column = 0
#            for content in fund:
#                content_for_fill = QtWidgets.QTableWidgetItem(content)
#                self.tableWidget_list.setItem(row, column, content_for_fill)
#                column += 1
            row += 1
#        self.tableWidget_list.resizeColumnsToContents()
