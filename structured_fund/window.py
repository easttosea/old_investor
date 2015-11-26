# -*- coding: utf-8 -*-
from structured_fund.ui import Ui_Form
from PyQt5 import QtWidgets, QtCore
from PyQt5 import QtGui


class MyWindow(QtWidgets.QMainWindow, Ui_Form):
    signal_fill_table_list = QtCore.pyqtSignal(list)
    signal_fill_table_handicap = QtCore.pyqtSignal()
    signal_statusbar_showmessage = QtCore.pyqtSignal(str)

    def __init__(self):
        super(MyWindow, self).__init__()
        self.setupUi(self)
        self.data_frame = None
        self.cell_row = 0
        self.tableWidget_list.setHorizontalHeaderLabels(
            ['代码', '名称', '现价',  '涨幅', '成交额', '净值', '溢价率', '利率规则', '本期利率', '下期利率',
             '修正收益率'])
        self.tableWidget_handicap.setVerticalHeaderLabels(
            ['卖五', '卖四', '卖三', '卖二', '卖一', '买一', '买二', '买三', '买四', '买五'])
        self.statusBar().showMessage('准备开始')
        self.signal_fill_table_list.connect(self.fill_table_list)
        self.signal_fill_table_handicap.connect(self.fill_table_handicap)
        self.signal_statusbar_showmessage.connect(self.statusBar().showMessage)
        self.tableWidget_list.cellClicked['int', 'int'].connect(self.fill_table_handicap)
        self.COLOR_RED = QtGui.QColor(200, 0, 0)
        self.COLOR_GREEN = QtGui.QColor(20, 150, 53)

    def fill_table_list(self, a_volume_0):
        data_list = list(self.data_frame.loc[:, [
            'a_code', 'a_name', 'a_price', 'a_increase_rate', 'a_increase_value', 'a_amount',
            'a_net_value', 'a_premium_rate', 'rate_rule', 'current_annual_rate', 'next_annual_rate',
            'modified_rate_of_return']].values)
        self.tableWidget_list.setRowCount(len(data_list))
        row = 0
        for fund in data_list:
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
            row += 1

    def fill_table_handicap(self, cell_row=None, cell_column=None):
        if cell_row is not None:
            self.cell_row = cell_row

        data_handicap = list(self.data_frame.loc[:, [
            'a_a5_p', 'a_a5_v', 'a_a4_p', 'a_a4_v', 'a_a3_p', 'a_a3_v', 'a_a2_p', 'a_a2_v', 'a_a1_p',
            'a_a1_v', 'a_b1_p', 'a_b1_v', 'a_b2_p', 'a_b2_v', 'a_b3_p', 'a_b3_v', 'a_b4_p', 'a_b4_v',
            'a_b5_p', 'a_b5_v', 'a_high', 'a_low', 'a_pre_close', 'a_open']].values)
        row = 0
        column = 0
        for data in data_handicap[self.cell_row]:
            cell = QtWidgets.QTableWidgetItem(str(data))
            cell.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            self.tableWidget_handicap.setItem(row, column, cell)
            column += 1
            if column > 1:
                column = 0
                row += 1
