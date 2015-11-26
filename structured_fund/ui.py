# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1920, 1000)
        self.tableWidget_handicap = QtWidgets.QTableWidget(Form)
        self.tableWidget_handicap.setEnabled(True)
        self.tableWidget_handicap.setGeometry(QtCore.QRect(1460, 10, 420, 400))
        self.tableWidget_handicap.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableWidget_handicap.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.tableWidget_handicap.setShowGrid(False)
        self.tableWidget_handicap.setGridStyle(QtCore.Qt.NoPen)
        self.tableWidget_handicap.setWordWrap(True)
        self.tableWidget_handicap.setCornerButtonEnabled(True)
        self.tableWidget_handicap.setRowCount(10)
        self.tableWidget_handicap.setColumnCount(2)
        self.tableWidget_handicap.setObjectName("tableWidget_handicap")
        self.tableWidget_handicap.horizontalHeader().setVisible(False)
        self.tableWidget_handicap.horizontalHeader().setDefaultSectionSize(60)
        self.tableWidget_handicap.verticalHeader().setVisible(True)
        self.tableWidget_handicap.verticalHeader().setCascadingSectionResizes(False)
        self.tableWidget_handicap.verticalHeader().setDefaultSectionSize(30)
        self.tableWidget_list = QtWidgets.QTableWidget(Form)
        self.tableWidget_list.setGeometry(QtCore.QRect(10, 10, 1400, 900))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.tableWidget_list.setFont(font)
        self.tableWidget_list.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableWidget_list.setAlternatingRowColors(False)
        self.tableWidget_list.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tableWidget_list.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableWidget_list.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerItem)
        self.tableWidget_list.setShowGrid(False)
        self.tableWidget_list.setGridStyle(QtCore.Qt.SolidLine)
        self.tableWidget_list.setWordWrap(True)
        self.tableWidget_list.setCornerButtonEnabled(True)
        self.tableWidget_list.setRowCount(0)
        self.tableWidget_list.setColumnCount(11)
        self.tableWidget_list.setObjectName("tableWidget_list")
        self.tableWidget_list.horizontalHeader().setVisible(True)
        self.tableWidget_list.horizontalHeader().setDefaultSectionSize(80)
        self.tableWidget_list.verticalHeader().setVisible(False)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "分级基金"))
        self.tableWidget_handicap.setSortingEnabled(False)
        self.tableWidget_list.setSortingEnabled(False)

