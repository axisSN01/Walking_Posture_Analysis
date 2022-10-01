# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'videoPlayer.ui'
#
# Created: Sat May 03 19:56:14 2014
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

class Ui_video(object):
    def setupUi(self, video):
        video.setObjectName(_fromUtf8("video"))
        video.resize(640, 526)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8("iconos/video.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        video.setWindowIcon(icon)
        self.videoPlayer = phonon.Phonon.VideoPlayer(video)
        self.videoPlayer.setGeometry(QtCore.QRect(-1, -1, 640, 480))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.videoPlayer.sizePolicy().hasHeightForWidth())
        self.videoPlayer.setSizePolicy(sizePolicy)
        self.videoPlayer.setCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))
        self.videoPlayer.setObjectName(_fromUtf8("videoPlayer"))
        self.bot_play = QtGui.QPushButton(video)
        self.bot_play.setGeometry(QtCore.QRect(0, 500, 75, 23))
        self.bot_play.setObjectName(_fromUtf8("bot_play"))
        self.bot_pause = QtGui.QPushButton(video)
        self.bot_pause.setGeometry(QtCore.QRect(100, 500, 75, 23))
        self.bot_pause.setObjectName(_fromUtf8("bot_pause"))
        self.bot_stop = QtGui.QPushButton(video)
        self.bot_stop.setGeometry(QtCore.QRect(200, 500, 75, 23))
        self.bot_stop.setObjectName(_fromUtf8("bot_stop"))

        self.retranslateUi(video)
        QtCore.QObject.connect(self.bot_play, QtCore.SIGNAL(_fromUtf8("clicked()")), self.videoPlayer.play)
        QtCore.QObject.connect(self.bot_pause, QtCore.SIGNAL(_fromUtf8("clicked()")), self.videoPlayer.pause)
        QtCore.QObject.connect(self.bot_stop, QtCore.SIGNAL(_fromUtf8("clicked()")), self.videoPlayer.stop)
        QtCore.QMetaObject.connectSlotsByName(video)

    def retranslateUi(self, video):
        video.setWindowTitle(_translate("video", "video", None))
        self.bot_play.setText(_translate("video", "play", None))
        self.bot_pause.setText(_translate("video", "pause", None))
        self.bot_stop.setText(_translate("video", "stop", None))

from PyQt4 import phonon
