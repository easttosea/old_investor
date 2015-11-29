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
        self.tableWidget_handicap_a = QtWidgets.QTableWidget(Form)
        self.tableWidget_handicap_a.setEnabled(True)
        self.tableWidget_handicap_a.setGeometry(QtCore.QRect(1460, 10, 220, 400))
        self.tableWidget_handicap_a.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.tableWidget_handicap_a.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableWidget_handicap_a.setTabKeyNavigation(False)
        self.tableWidget_handicap_a.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.tableWidget_handicap_a.setShowGrid(False)
        self.tableWidget_handicap_a.setGridStyle(QtCore.Qt.NoPen)
        self.tableWidget_handicap_a.setWordWrap(True)
        self.tableWidget_handicap_a.setCornerButtonEnabled(True)
        self.tableWidget_handicap_a.setRowCount(10)
        self.tableWidget_handicap_a.setColumnCount(2)
        self.tableWidget_handicap_a.setObjectName("tableWidget_handicap_a")
        self.tableWidget_handicap_a.horizontalHeader().setVisible(False)
        self.tableWidget_handicap_a.horizontalHeader().setDefaultSectionSize(60)
        self.tableWidget_handicap_a.verticalHeader().setVisible(True)
        self.tableWidget_handicap_a.verticalHeader().setCascadingSectionResizes(False)
        self.tableWidget_handicap_a.verticalHeader().setDefaultSectionSize(30)
        self.tableWidget_list = QtWidgets.QTableWidget(Form)
        self.tableWidget_list.setGeometry(QtCore.QRect(10, 10, 1400, 900))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.tableWidget_list.setFont(font)
        self.tableWidget_list.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableWidget_list.setAlternatingRowColors(True)
        self.tableWidget_list.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tableWidget_list.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableWidget_list.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerItem)
        self.tableWidget_list.setShowGrid(False)
        self.tableWidget_list.setGridStyle(QtCore.Qt.SolidLine)
        self.tableWidget_list.setWordWrap(True)
        self.tableWidget_list.setCornerButtonEnabled(True)
        self.tableWidget_list.setObjectName("tableWidget_list")
        self.tableWidget_list.horizontalHeader().setVisible(True)
        self.tableWidget_list.horizontalHeader().setDefaultSectionSize(80)
        self.tableWidget_list.verticalHeader().setVisible(False)
        self.tableWidget_handicap_b = QtWidgets.QTableWidget(Form)
        self.tableWidget_handicap_b.setEnabled(True)
        self.tableWidget_handicap_b.setGeometry(QtCore.QRect(1690, 10, 220, 400))
        self.tableWidget_handicap_b.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.tableWidget_handicap_b.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableWidget_handicap_b.setTabKeyNavigation(False)
        self.tableWidget_handicap_b.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.tableWidget_handicap_b.setShowGrid(False)
        self.tableWidget_handicap_b.setGridStyle(QtCore.Qt.NoPen)
        self.tableWidget_handicap_b.setWordWrap(True)
        self.tableWidget_handicap_b.setCornerButtonEnabled(True)
        self.tableWidget_handicap_b.setRowCount(10)
        self.tableWidget_handicap_b.setColumnCount(2)
        self.tableWidget_handicap_b.setObjectName("tableWidget_handicap_b")
        self.tableWidget_handicap_b.horizontalHeader().setVisible(False)
        self.tableWidget_handicap_b.horizontalHeader().setDefaultSectionSize(60)
        self.tableWidget_handicap_b.verticalHeader().setVisible(True)
        self.tableWidget_handicap_b.verticalHeader().setCascadingSectionResizes(False)
        self.tableWidget_handicap_b.verticalHeader().setDefaultSectionSize(30)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "分级基金"))
        self.tableWidget_handicap_a.setSortingEnabled(False)
        self.tableWidget_list.setSortingEnabled(False)
        self.tableWidget_handicap_b.setSortingEnabled(False)

