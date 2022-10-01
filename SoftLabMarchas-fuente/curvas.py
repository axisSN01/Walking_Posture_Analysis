# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'curvas.ui'
#
# Created: Fri May 02 17:15:28 2014
#      by: PyQt4 UI code generator 4.9.6
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_curvas(object):
    def setupUi(self, curvas):
        curvas.setObjectName(_fromUtf8("curvas"))
        curvas.resize(520, 495)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(curvas.sizePolicy().hasHeightForWidth())
        curvas.setSizePolicy(sizePolicy)
        curvas.setMinimumSize(QtCore.QSize(520, 495))
        curvas.setMaximumSize(QtCore.QSize(522, 496))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8("iconos/UNNe2.jpg")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        curvas.setWindowIcon(icon)
        self.textBrowser = QtGui.QTextBrowser(curvas)
        self.textBrowser.setGeometry(QtCore.QRect(9, 9, 501, 481))
        self.textBrowser.setObjectName(_fromUtf8("textBrowser"))

        self.retranslateUi(curvas)
        QtCore.QMetaObject.connectSlotsByName(curvas)

    def retranslateUi(self, curvas):
        curvas.setWindowTitle(_translate("curvas", "curvas", None))

