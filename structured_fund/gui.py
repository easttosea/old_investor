# -*- coding: utf-8 -*-
from structured_fund.ui import Ui_Form
from PyQt5 import QtWidgets, QtCore
from PyQt5 import QtGui


class MyWindow(QtWidgets.QMainWindow, Ui_Form):
    signal_fill_table_list = QtCore.pyqtSignal()
    signal_fill_table_handicap = QtCore.pyqtSignal()
    signal_statusbar_showmessage = QtCore.pyqtSignal(str)

    def __init__(self):
        super(MyWindow, self).__init__()
        self.setupUi(self)
        self.frame_realtime = None
        self.sort_column = 'modified_rate_of_return'
        self.sort_ascending = False
        self.cell_row = 0
        self.selected_m_code = ''
        self.selected_a_code = ''
        self.selected_b_code = ''
        self.tableWidget_list.setRowCount(0)
        self.tableWidget_list.setColumnCount(14)
        self.tableWidget_list.setHorizontalHeaderLabels(
            ['代码', '名称', '现价',  '涨幅', '成交额', '净值', '溢价率', '利率规则', '本期利率', '下期利率',
             '修正收益率', '参考指数', '指数涨幅', '下折母基需跌'])
        self.tableWidget_handicap_a.setVerticalHeaderLabels(
            ['卖五', '卖四', '卖三', '卖二', '卖一', '买一', '买二', '买三', '买四', '买五'])
        self.signal_fill_table_list.connect(self.fill_table_list)
        self.signal_fill_table_handicap.connect(self.fill_table_handicap)
        self.tableWidget_list.cellClicked['int', 'int'].connect(self.cell_clicked)
        self.tableWidget_list.horizontalHeader().sectionClicked.connect(self.horizon_section_clicked)
        self.signal_statusbar_showmessage.connect(self.statusBar().showMessage)
        self.COLOR_RED = QtGui.QColor(200, 0, 0)
        self.COLOR_GREEN = QtGui.QColor(20, 150, 53)
        self.COLOR_GRAY = QtGui.QColor(200, 200, 200)
        self.RATE_RULE_SHOW = {'1年+3.0%': QtGui.QColor(200, 0, 0), '1年+3.2%':QtGui.QColor(200, 128, 0),
                               '1年+3.5%':QtGui.QColor(200, 200, 0), '固定5.0%':QtGui.QColor(200, 200, 0),
                               '1年+4.0%':QtGui.QColor(128, 200, 0), '固定5.8%':QtGui.QColor(128, 200, 0),
                               '1年+4.5%':QtGui.QColor(0, 200, 0), '固定6.0%':QtGui.QColor(0, 200, 0),
                               '1年+5.0%':QtGui.QColor(0, 200, 128), '固定7.0%':QtGui.QColor(0, 200, 200)}

    def fill_table_list(self):
        self.frame_realtime = self.frame_realtime.sort_values(by=self.sort_column, ascending=self.sort_ascending)
        if self.selected_m_code == '':
            self.selected_m_code = self.frame_realtime.index[0]
        # Format the data to strings
        frame_list = self.frame_realtime.loc[:, [
            'a_code', 'a_name', 'a_price', 'a_increase_rate', 'a_amount',
            'a_net_value', 'a_premium_rate', 'rate_rule', 'current_annual_rate', 'next_annual_rate',
            'modified_rate_of_return', 'i_name', 'i_increase_rate', 'm_descending_distance']]
        frame_list['a_price'] = frame_list['a_price'].map(lambda x: '%.3f' % x)
        frame_list['a_increase_rate'] = frame_list['a_increase_rate'].map(lambda x: '%.2f%%' % (x*100))
        frame_list['a_amount'] = frame_list['a_amount'].map(lambda x: '%.1f万' % (x/10000))
        frame_list['a_net_value'] = frame_list['a_net_value'].map(lambda x: '%.3f' % x)
        frame_list['a_premium_rate'] = frame_list['a_premium_rate'].map(lambda x: '%.2f%%' % (x*100))
        frame_list['current_annual_rate'] = frame_list['current_annual_rate'].map(
            lambda x: '%.2f%%' % (x*100))
        frame_list['next_annual_rate'] = frame_list['next_annual_rate'].map(lambda x: '%.2f%%' % (x*100))
        frame_list['modified_rate_of_return'] = frame_list['modified_rate_of_return'].map(
            lambda x: '%.3f%%' % (x*100))
        for index in list(self.frame_realtime[self.frame_realtime.a_net_value == 0].index):
            frame_list.loc[index, ['a_net_value', 'a_premium_rate', 'modified_rate_of_return']] = '-'
        frame_list['i_increase_rate'] = frame_list['i_increase_rate'].map(lambda x: '%.2f%%' % (x*100))
        frame_list['m_descending_distance'] = frame_list['m_descending_distance'].map(
            lambda num: '%.2f%%' % (num * 100))
        # Fill in the table of fund list
        data_list = list(frame_list.values)
        self.tableWidget_list.setRowCount(len(data_list))
        row = 0
        for fund in data_list:
            a_code = QtWidgets.QTableWidgetItem(fund[0])
            a_name = QtWidgets.QTableWidgetItem(fund[1])
            a_price = QtWidgets.QTableWidgetItem(fund[2])
            a_increase_rate = QtWidgets.QTableWidgetItem(fund[3])
            a_amount = QtWidgets.QTableWidgetItem(fund[4])
            a_net_value = QtWidgets.QTableWidgetItem(fund[5])
            a_premium_rate = QtWidgets.QTableWidgetItem(fund[6])
            rate_rule = QtWidgets.QTableWidgetItem(fund[7])
            current_annual_rate = QtWidgets.QTableWidgetItem(fund[8])
            next_annual_rate = QtWidgets.QTableWidgetItem(fund[9])
            modified_rate_of_return = QtWidgets.QTableWidgetItem(fund[10])
            i_name = QtWidgets.QTableWidgetItem(fund[11])
            i_increase_rate = QtWidgets.QTableWidgetItem(fund[12])
            m_descending_distance = QtWidgets.QTableWidgetItem(fund[13])
            cell_list = [a_code, a_name, a_price, a_increase_rate, a_amount, a_net_value, a_premium_rate, rate_rule,
                         current_annual_rate, next_annual_rate, modified_rate_of_return, i_name,
                         i_increase_rate, m_descending_distance]
            if fund[7] in self.RATE_RULE_SHOW:
                rate_rule.setForeground(self.RATE_RULE_SHOW[fund[7]])
            if self.frame_realtime.a_increase_rate[row] > 0:
                a_price.setForeground(self.COLOR_RED)
                a_increase_rate.setForeground(self.COLOR_RED)
            elif self.frame_realtime.a_increase_rate[row] < 0:
                a_price.setForeground(self.COLOR_GREEN)
                a_increase_rate.setForeground(self.COLOR_GREEN)
            if self.frame_realtime.years_to_delist_date[row] > 0:
                modified_rate_of_return.setText('{0:.2f}年到期'.format(self.frame_realtime.years_to_delist_date[row]))
                modified_rate_of_return.setForeground(self.COLOR_GRAY)
            if self.frame_realtime.isnull().i_increase_rate[row]:
                i_increase_rate.setText('-')
            if self.frame_realtime.i_increase_rate[row] > 0:
                i_increase_rate.setForeground(self.COLOR_RED)
            elif self.frame_realtime.i_increase_rate[row] < 0:
                i_increase_rate.setForeground(self.COLOR_GREEN)
            if fund[0] in self.frame_realtime.a_code[self.frame_realtime.a_volume == 0]:
                for cell in cell_list:
                    cell.setForeground(self.COLOR_GRAY)
            if self.frame_realtime.isnull().m_descending_distance[row]:
                m_descending_distance.setText('无下折')
                m_descending_distance.setForeground(self.COLOR_GRAY)
            column = 0
            for cell in cell_list:
                cell.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
                self.tableWidget_list.setItem(row, column, cell)
                column += 1
            row += 1
        self.tableWidget_list.selectRow(list(self.frame_realtime.index).index(self.selected_m_code))

    def horizon_section_clicked(self, index):
        columns = ['a_code', 'a_name', 'a_price', 'a_increase_rate', 'a_amount', 'a_net_value',
                   'a_premium_rate', 'rate_rule', 'current_annual_rate', 'next_annual_rate',
                   'modified_rate_of_return', 'i_name', 'i_increase_rate',
                   'm_descending_distance']
        if self.sort_column == columns[index]:
            if self.sort_ascending is True:
                self.sort_ascending = False
            else:
                self.sort_ascending = True
        else:
            self.sort_column = columns[index]
            self.sort_ascending = False
        self.fill_table_list()

    def cell_clicked(self, cell_row=None, cell_column=None):
        self.selected_m_code = self.frame_realtime.index[cell_row]
#        self.selected_a_code = self.frame_realtime.at[self.selected_m_code, 'a_code']
#        self.selected_b_code = self.frame_realtime.at[self.selected_m_code, 'b_code']
        self.fill_table_handicap()

    def fill_table_handicap(self):
        a_pre_close = self.frame_realtime.at[self.selected_m_code, 'a_pre_close']
        frame_handicap = self.frame_realtime.loc[self.selected_m_code, [
            'a_a5_p', 'a_a5_v', 'a_a4_p', 'a_a4_v', 'a_a3_p', 'a_a3_v', 'a_a2_p', 'a_a2_v', 'a_a1_p',
            'a_a1_v', 'a_b1_p', 'a_b1_v', 'a_b2_p', 'a_b2_v', 'a_b3_p', 'a_b3_v', 'a_b4_p', 'a_b4_v',
            'a_b5_p', 'a_b5_v']]
        data_a_list = list(frame_handicap.values)
        row = 0
        for data_serial in range(0, len(data_a_list), 2):
            cell_price = QtWidgets.QTableWidgetItem('%.3f' % data_a_list[data_serial])
            cell_volume = QtWidgets.QTableWidgetItem(str(data_a_list[data_serial + 1]))
            if data_a_list[data_serial] == 0.0:
                cell_price = QtWidgets.QTableWidgetItem('-')
                cell_volume = QtWidgets.QTableWidgetItem('-')
#                cell_price.setForeground(self.COLOR_GRAY)
#                cell_volume.setForeground(self.COLOR_GRAY)
            elif data_a_list[data_serial] > a_pre_close:
                cell_price.setForeground(self.COLOR_RED)
                cell_volume.setForeground(self.COLOR_RED)
            elif data_a_list[data_serial] < a_pre_close:
                cell_price. setForeground(self.COLOR_GREEN)
                cell_volume. setForeground(self.COLOR_GREEN)
            cell_price.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            cell_volume.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            self.tableWidget_handicap_a.setItem(row, 0, cell_price)
            self.tableWidget_handicap_a.setItem(row, 1, cell_volume)
            row += 1
