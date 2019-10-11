#!/usr/bin/env python3

from PyQt5.QtCore import *
#from PyQt5.QtGui import QPixmap
#from PyQt5.QtWidgets import QMainWindow, QApplication, QSizePolicy
from PyQt5.QtWidgets import QDial,QGroupBox, QLabel,QVBoxLayout
#from PyQt5.QtMultimedia import QCamera, QCameraImageCapture,QVideoFrame,QAbstractVideoBuffer,QCameraInfo
#from TIFgrabUI import Ui_TIFgrabMW
#import sys, signal, os
#from glob import glob
#from configparser import ConfigParser
#import pyudev.pyqt5
#import pyudev

#signal.signal(signal.SIGINT, signal.SIG_DFL)
    
class TimerGB(QGroupBox):

    grab_timeout = pyqtSignal()
    gb_closed = pyqtSignal()
    
    def __init__(self, boxwidth, boxheight, parent=None):
        super(TimerGB, self).__init__(parent)
        QGroupBox("Set Interval")

        self.resize(boxwidth, boxheight)
        
        self.setWindowTitle("Timer")
        self.setFlat(True)
        
        self.timer_dial = QDial()
        self.timer_dial.setNotchesVisible(True)
        self.timer_dial.setMinimum(1)
        self.timer_dial.setMaximum(30)
        self.timer_dial.setValue(15)
        self.timer_dial.valueChanged.connect(self.on_dial_new_value)
        self.timer_dial.sliderReleased.connect(self.on_dial_released)
            
        self.value_display = QLabel()
        self.gbvlayout = QVBoxLayout()
        self.gbvlayout.addWidget(self.value_display)
        self.gbvlayout.addWidget(self.timer_dial)
        self.setLayout(self.gbvlayout)
        self.value_display.setText(str(self.timer_dial.value()) + " s")

        self.grab_timer = QTimer()

    def on_dial_new_value(self):
        self.value_display.setText(str(self.timer_dial.value()) + " s")

    def on_dial_released(self):
        self.timer_rate = self.timer_dial.value()
        #print("Timer rate is ", self.timer_rate)
        self.grab_timer = QTimer()
#        self.grab_timer.timeout.connect(self.on_grab_button)
        self.grab_timer.timeout.connect(self.on_grab_timer_timeout)
        self.grab_timer.start(self.timer_rate * 1000.0)

    def on_grab_timer_timeout(self):
        self.grab_timeout.emit()

    def closeEvent(self, event):
        self.gb_closed.emit()

    def get_width(self):
        return self.width()
    def get_height(self):
        return self.height()
