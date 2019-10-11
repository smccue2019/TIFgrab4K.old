# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'TIFgrabUI.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_TIFgrabMW(object):
    def setupUi(self, TIFgrabMW):
        TIFgrabMW.setObjectName("TIFgrabMW")
        TIFgrabMW.resize(800, 422)
        self.centralwidget = QtWidgets.QWidget(TIFgrabMW)
        self.centralwidget.setMaximumSize(QtCore.QSize(900, 400))
        self.centralwidget.setObjectName("centralwidget")
        self.grabButton = QtWidgets.QPushButton(self.centralwidget)
        self.grabButton.setGeometry(QtCore.QRect(630, 50, 99, 27))
        self.grabButton.setObjectName("grabButton")
        self.quitButton = QtWidgets.QPushButton(self.centralwidget)
        self.quitButton.setGeometry(QtCore.QRect(630, 280, 99, 27))
        self.quitButton.setObjectName("quitButton")
        self.FilenameDisp = QtWidgets.QLabel(self.centralwidget)
        self.FilenameDisp.setGeometry(QtCore.QRect(110, 340, 611, 17))
        font = QtGui.QFont()
        font.setItalic(True)
        self.FilenameDisp.setFont(font)
        self.FilenameDisp.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.FilenameDisp.setObjectName("FilenameDisp")
        self.ThumbnailFrame = QtWidgets.QFrame(self.centralwidget)
        self.ThumbnailFrame.setGeometry(QtCore.QRect(100, 30, 480, 270))
        self.ThumbnailFrame.setFrameShape(QtWidgets.QFrame.Box)
        self.ThumbnailFrame.setFrameShadow(QtWidgets.QFrame.Plain)
        self.ThumbnailFrame.setLineWidth(4)
        self.ThumbnailFrame.setObjectName("ThumbnailFrame")
        self.ThumbnailView = QtWidgets.QLabel(self.ThumbnailFrame)
        self.ThumbnailView.setGeometry(QtCore.QRect(0, 0, 480, 270))
        self.ThumbnailView.setObjectName("ThumbnailView")
        self.TimerRadio = QtWidgets.QRadioButton(self.centralwidget)
        self.TimerRadio.setGeometry(QtCore.QRect(630, 90, 117, 22))
        self.TimerRadio.setObjectName("TimerRadio")
        self.PicStats = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.PicStats.setGeometry(QtCore.QRect(600, 140, 131, 111))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.PicStats.setFont(font)
        self.PicStats.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.PicStats.setFrameShadow(QtWidgets.QFrame.Plain)
        self.PicStats.setObjectName("PicStats")
        self.Sourcename_Disp = QtWidgets.QLabel(self.centralwidget)
        self.Sourcename_Disp.setGeometry(QtCore.QRect(100, 300, 481, 17))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.Sourcename_Disp.setFont(font)
        self.Sourcename_Disp.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.Sourcename_Disp.setObjectName("Sourcename_Disp")
        TIFgrabMW.setCentralWidget(self.centralwidget)

        self.retranslateUi(TIFgrabMW)
        QtCore.QMetaObject.connectSlotsByName(TIFgrabMW)

    def retranslateUi(self, TIFgrabMW):
        _translate = QtCore.QCoreApplication.translate
        TIFgrabMW.setWindowTitle(_translate("TIFgrabMW", "TIFgrab"))
        self.grabButton.setText(_translate("TIFgrabMW", "Grab"))
        self.quitButton.setText(_translate("TIFgrabMW", "Quit"))
        self.FilenameDisp.setText(_translate("TIFgrabMW", "Saved image filename"))
        self.ThumbnailView.setText(_translate("TIFgrabMW", "Gimme something"))
        self.TimerRadio.setText(_translate("TIFgrabMW", "Timer"))
        self.Sourcename_Disp.setText(_translate("TIFgrabMW", "Capture card and camera source info"))

