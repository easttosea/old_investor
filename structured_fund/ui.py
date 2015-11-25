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
        Form.resize(1200, 800)
        self.tableWidget_list = QtWidgets.QTableWidget(Form)
        self.tableWidget_list.setGeometry(QtCore.QRect(50, 50, 1100, 700))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.tableWidget_list.setFont(font)
        self.tableWidget_list.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableWidget_list.setAlternatingRowColors(True)
        self.tableWidget_list.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tableWidget_list.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableWidget_list.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerItem)
        self.tableWidget_list.setShowGrid(True)
        self.tableWidget_list.setRowCount(150)
        self.tableWidget_list.setColumnCount(15)
        self.tableWidget_list.setObjectName("tableWidget_list")
        self.tableWidget_list.horizontalHeader().setDefaultSectionSize(80)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "分级基金"))
        self.tableWidget_list.setSortingEnabled(False)

