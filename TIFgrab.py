#!/usr/bin/env python3

from PyQt5.QtCore import *
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMainWindow, QApplication, QSizePolicy
#from PyQt5.QtWidgets import QDial,QGroupBox, QLabel,QVBoxLayout
from PyQt5.QtWidgets import QLabel
from PyQt5.QtMultimedia import QCamera, QCameraImageCapture,QVideoFrame,QAbstractVideoBuffer,QCameraInfo
from TIFgrabUI import Ui_TIFgrabMW
import sys, signal, os
from glob import glob
from configparser import ConfigParser
import pyudev
from timergb import TimerGB

signal.signal(signal.SIGINT, signal.SIG_DFL)
    
class TIFgrabGUI(QMainWindow):
    def __init__(self, capcard_full, capcard_short, parent=None):
        super(TIFgrabGUI, self).__init__(parent)


        self.cleanup_side_captures()
        
        # set up GUI from designer-made layout
        self.ui = Ui_TIFgrabMW()
        self.ui.setupUi(self)

        # Temporarily? hard code the device definition
        self.sys_device = "/dev/video0"
        target_cam_serialnum = capcard_short[self.sys_device]
        target_cam_label = capcard_full[self.sys_device]

        print("Targeting camera device ", self.sys_device)
        print("Labeling as ", target_cam_label)
        
        self.picframe_width=self.ui.ThumbnailView.frameGeometry().width()
        self.picframe_height=self.ui.ThumbnailView.frameGeometry().height()

        
        #for device_name in QCamera.availableDevices():
        #    print("Looking at", device_name)
        #    if (device_name == target_cam_dev):
        #self.camera_device = device_name
#        self.camera_device = target_cam_dev.encode('utf-8')
        self.camera_device = self.sys_device.encode('utf-8')
        self.camera_label = target_cam_label
        self.ui.Sourcename_Disp.setText(self.camera_label)
        self.cam1 = QCamera(self.camera_device)
        
#        self.cam1_info = QCameraInfo(self.cam1)
#        self.cam1_nonhuman_name = self.cam1_info.deviceName()
#        print("Description= ",self.cam1_info.description())
#        print("Nonhuman= ", self.cam1_info.deviceName())
        
        self.cam1_capture = QCameraImageCapture(self.cam1)
        print("Still image capture from device %s, capture card %s)" % (self.camera_device, self.camera_label))

        self.cam1.setCaptureMode(QCamera.CaptureStillImage)
        self.cam1_capture.setCaptureDestination(QCameraImageCapture.CaptureToBuffer)

        #### Assign a startup image ####
        # print('Displaying startup image')
        #self.tifimage = QPixmap('/home/scotty/src/GrabDev/tasman_island_lighthouse.tif', 'tif')
        self.tifimage = QPixmap('./tasman_island_lighthouse.tif', 'tif')
        self.thumb = self.tifimage.scaled(self.picframe_width,self.picframe_height, Qt.KeepAspectRatio)
        self.ui.ThumbnailView.setScaledContents(True)
        self.ui.ThumbnailView.setPixmap(self.thumb)

        # Set event handlers
        self.ui.grabButton.clicked.connect(self.on_grab_button)
        self.ui.TimerRadio.toggled.connect(self.on_timerradio_button)
        self.ui.quitButton.clicked.connect(self.on_quit_button)
        self.cam1_capture.imageCaptured.connect(self.on_image_captured)

        self.ui.FilenameDisp.setText("No image captured")
        self.cam1.start()
        
    def on_grab_button(self):
        self.cam1.searchAndLock()
        self.capture_time = systime()
        self.capture_name = "./" + self.camera_label + "_" + self.capture_time + ".tif"
        self.cam1_capture.capture()
        self.cam1.unlock()

    def on_image_captured(self,id,captured_image):
        # The image to be displayed on screen
        self.captured2pixmap = QPixmap()
        success=self.captured2pixmap.convertFromImage(captured_image)

        self.list_pic_stats()
        
        self.thumb_scaled = self.captured2pixmap.scaled(self.picframe_width,self.picframe_height, Qt.KeepAspectRatio)
        self.ui.ThumbnailView.setScaledContents(True)
        self.ui.ThumbnailView.setSizePolicy(QSizePolicy.Ignored,QSizePolicy.Ignored)
        self.ui.FilenameDisp.setText(self.capture_name)
        self.ui.ThumbnailView.setPixmap(self.thumb_scaled)

        # The image to be saved to file as TIF
        # First confirm that the destination folder exists, create if it doesn't.
        self.manage_daily_folder()
        self.capture_fullpath = self.outdirname + "/" + self.capture_name
        outimage = QPixmap()
        outimage.convertFromImage(captured_image)
        outfile = QFile(self.capture_fullpath)
        outfile.open(QIODevice.WriteOnly)
        outimage.save(outfile, "TIFF")
        outfile.close()

    def list_pic_stats(self):

        sizestr = ("Size: %d X %d") %  (self.captured2pixmap.width(),self.captured2pixmap.height())
        depthstr = ("Depth:%s ") % (self.captured2pixmap.depth())
        bmapstr = ("Is Bitmap?:%s") % (self.captured2pixmap.isQBitmap())
        alphastr = ("Has alpha?:%s") % (self.captured2pixmap.hasAlphaChannel())
        self.ui.PicStats.setPlainText(self.sys_device)
        self.ui.PicStats.appendPlainText(sizestr)
        self.ui.PicStats.appendPlainText(depthstr)
        
    def on_timerradio_button(self):
        if self.ui.TimerRadio.isChecked():
            self.ui.grabButton.setEnabled(False)
            self.add_timer_groupbox()
        if not self.ui.TimerRadio.isChecked():
           if self.timergb:
                self.timergb.grab_timer.stop()
                self.ui.grabButton.setEnabled(True)
                self.timergb.deleteLater()
                self.timergb = None
                
    def add_timer_groupbox(self):

        self.timergb = TimerGB(75,100)
        self.timergb.grab_timeout.connect(self.on_grab_button)
        self.timergb.gb_closed.connect(self.on_timergb_closed)
        self.timergb.show()

    def on_timergb_closed(self):
        if self.ui.TimerRadio.isChecked():
            if self.timergb:
           #     self.grab_timer.stop()
                self.timergb.deleteLater()
                self.timergb = None
                self.ui.TimerRadio.setChecked(False)
                self.ui.grabButton.setEnabled(True)
        
    def cleanup_side_captures(self):
        # Remove jpgs saved by QCameraImageCapture in default location
        defaultlocation = "/home/jason/Pictures"
        print("Removing all jpgs from ", defaultlocation)
        fullpath=("%s/*.jpg") % (defaultlocation)
        for filename in glob(fullpath):
            print("Removing ", filename)
            os.remove(filename)
            
    def on_quit_button(self):
        self.cam1.stop()
        try:
            if self.timergb:
                self.timergb.deleteLater()
                self.timergb = None
        except:
            pass

        self.cleanup_side_captures()
        
        QCoreApplication.exit()

    def sigint_handler(*args):
        try:
            if self.timergb:
                self.timergb.deleteLater()
                self.timergb = None
        except:
            pass
        sys.stderr.write('\r')
        QApplication.quit()

    def do_init(ini_filename):
        cf = ConfigParser()
        cf.read(ini_filename)

    def manage_daily_folder(self):
        # Tests for existence of folder to hold the date's captures.
        # If folder doesn't exist, creates it.
        today = sysdate()

        self.outdirname="/data/capture_" + today
        if not os.path.exists(self.outdirname):
            os.makedirs(self.outdirname)
        

if __name__ == "__main__":

    # Minor config here. User defines config filename.
    ini_filename = "tifgrab.ini"

    # User assigns camera label in config file.
    # Labeling is matched to an Epiphan serial number. 
    # do_init() matches label to device, e.g., "/dev/video1"
#    cam_label, cam_device = do_init(ini_filename)


    app = QApplication(sys.argv)
    
    try:
        exec(open("./time_routines.py").read())
    except Exception as e:
        print("Error opening or running time_routines.py", e)

    try:
        exec(open("./udev_routines.py").read())
    except Exception as e:
        print("Error opening or running udev_routines.py", e)

    cap_devices_full_serial, cap_devices_short_serial = get_v4l_device_list()

#    gd=TIFgrabGUI(cam_label,cam_device)
    gd=TIFgrabGUI(cap_devices_full_serial, cap_devices_short_serial)
    gd.show()
        
    sys.exit(app.exec_())
