# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'WebElementDocs.ui'
#
# Created: Thu May 12 12:06:55 2011
#      by: PyQt4 UI code generator 4.6.2
#
# WARNING! All changes made in this file will be lost!

import os

from PyQt4 import QtCore, QtGui

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtGui.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.frame_2 = QtGui.QFrame(self.centralwidget)
        self.frame_2.setMinimumSize(QtCore.QSize(250, 0))
        self.frame_2.setMaximumSize(QtCore.QSize(250, 16777215))
        self.frame_2.setFrameShape(QtGui.QFrame.NoFrame)
        self.frame_2.setFrameShadow(QtGui.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.verticalLayout_8 = QtGui.QVBoxLayout(self.frame_2)
        self.verticalLayout_8.setSpacing(-1)
        self.verticalLayout_8.setMargin(0)
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.horizontalLayout_8 = QtGui.QHBoxLayout()
        self.horizontalLayout_8.setSpacing(1)
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.label = QtGui.QLabel(self.frame_2)
        self.label.setPixmap(QtGui.QPixmap(os.path.dirname(__file__) + "/icons/find.png"))
        self.label.setObjectName("label")
        self.horizontalLayout_8.addWidget(self.label)
        self.filter = QtGui.QLineEdit(self.frame_2)
        self.filter.setObjectName("filter")
        self.horizontalLayout_8.addWidget(self.filter)
        self.cancelFilter = QtGui.QToolButton(self.frame_2)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(os.path.dirname(__file__) + "/icons/cancel.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.cancelFilter.setIcon(icon)
        self.cancelFilter.setIconSize(QtCore.QSize(16, 16))
        self.cancelFilter.setAutoRaise(True)
        self.cancelFilter.setObjectName("cancelFilter")
        self.horizontalLayout_8.addWidget(self.cancelFilter)
        self.verticalLayout_8.addLayout(self.horizontalLayout_8)
        self.browserView = QtGui.QStackedWidget(self.frame_2)
        self.browserView.setObjectName("browserView")
        self.elementsFrame = QtGui.QWidget()
        self.elementsFrame.setObjectName("elementsFrame")
        self.gridLayout = QtGui.QGridLayout(self.elementsFrame)
        self.gridLayout.setMargin(0)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self.elements = QtGui.QToolBox(self.elementsFrame)
        self.elements.setObjectName("elements")
        self.page_4 = QtGui.QWidget()
        self.page_4.setGeometry(QtCore.QRect(0, 0, 250, 536))
        self.page_4.setObjectName("page_4")
        self.elements.addItem(self.page_4, "")
        self.gridLayout.addWidget(self.elements, 0, 0, 1, 1)
        self.browserView.addWidget(self.elementsFrame)
        self.page_7 = QtGui.QWidget()
        self.page_7.setObjectName("page_7")
        self.verticalLayout_12 = QtGui.QVBoxLayout(self.page_7)
        self.verticalLayout_12.setSpacing(0)
        self.verticalLayout_12.setMargin(0)
        self.verticalLayout_12.setObjectName("verticalLayout_12")
        self.searchResults = QtGui.QListWidget(self.page_7)
        self.searchResults.setDragDropMode(QtGui.QAbstractItemView.DragOnly)
        self.searchResults.setIconSize(QtCore.QSize(32, 32))
        self.searchResults.setObjectName("searchResults")
        self.verticalLayout_12.addWidget(self.searchResults)
        self.browserView.addWidget(self.page_7)
        self.verticalLayout_8.addWidget(self.browserView)
        self.horizontalLayout.addWidget(self.frame_2)
        self.info = QtGui.QTextBrowser(self.centralwidget)
        self.info.setFrameShape(QtGui.QFrame.NoFrame)
        self.info.setFrameShadow(QtGui.QFrame.Plain)
        self.info.setLineWidth(0)
        self.info.setObjectName("info")
        self.horizontalLayout.addWidget(self.info)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        self.browserView.setCurrentIndex(0)
        self.elements.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))
        self.frame_2.setStyleSheet(QtGui.QApplication.translate("MainWindow", "background-color:rgb(221, 221, 221);", None, QtGui.QApplication.UnicodeUTF8))
        self.filter.setStyleSheet(QtGui.QApplication.translate("MainWindow", "background-color:white;", None, QtGui.QApplication.UnicodeUTF8))
        self.cancelFilter.setText(QtGui.QApplication.translate("MainWindow", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.elements.setItemText(self.elements.indexOf(self.page_4), QtGui.QApplication.translate("MainWindow", "Page 2", None, QtGui.QApplication.UnicodeUTF8))
        self.info.setHtml(QtGui.QApplication.translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600; text-decoration: underline;\">&lt;----- Select element here to see detailed class documentation.</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">The WebElementDocs Browser allows you to see the class definitions of all webelements, for a more general overview of how the webelement framework works see: <span style=\" text-decoration: underline;\">http://wiki.arincdirect.net/bin/view/Adc/WebElementFramework</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))

