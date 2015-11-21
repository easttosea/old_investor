# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form_structured_fund(object):
    def setupUi(self, Form_structured_fund):
        Form_structured_fund.setObjectName("Form_structured_fund")
        Form_structured_fund.resize(1200, 800)
        self.tableWidget_structured_fund = QtWidgets.QTableWidget(Form_structured_fund)
        self.tableWidget_structured_fund.setGeometry(QtCore.QRect(50, 50, 1100, 700))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.tableWidget_structured_fund.setFont(font)
        self.tableWidget_structured_fund.setAlternatingRowColors(True)
        self.tableWidget_structured_fund.setRowCount(150)
        self.tableWidget_structured_fund.setColumnCount(15)
        self.tableWidget_structured_fund.setObjectName("tableWidget_structured_fund")

        self.retranslateUi(Form_structured_fund)
        QtCore.QMetaObject.connectSlotsByName(Form_structured_fund)

    def retranslateUi(self, Form_structured_fund):
        _translate = QtCore.QCoreApplication.translate
        Form_structured_fund.setWindowTitle(_translate("Form_structured_fund", "分级基金"))