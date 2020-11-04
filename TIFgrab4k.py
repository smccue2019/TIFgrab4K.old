#!/usr/bin/env python3

from PyQt5.QtCore import *
from PyQt5.QtGui import QPixmap, QImage, QColor
from PyQt5.QtWidgets import QMainWindow, QApplication, QSizePolicy
from PyQt5.QtWidgets import QLabel
from PyQt5.QtMultimedia import QCamera, QCameraImageCapture,QVideoFrame,QAbstractVideoBuffer,QCameraInfo,QImageEncoderSettings
from PyQt5.QtMultimedia import QCameraViewfinderSettings,QMediaMetaData
import sys, signal, os, traceback, re
from glob import glob
from configparser import ConfigParser
from sjm_pkg.timergb import TimerGB
from sjm_pkg.time_routines import mysystime, sysdate
from sjm_pkg.udev_routines import get_v4l_device_list
from sjm_pkg.sh import SmartHubComm

from TIFgrabUI import Ui_TIFgrabMW

signal.signal(signal.SIGINT, signal.SIG_DFL)
    
class TIFgrabGUI(QMainWindow):
    def __init__(self, capcard_full, capcard_short, inifname,parent=None):
        super(TIFgrabGUI, self).__init__(parent)

        self.do_init(inifname)
        self.cleanup_side_captures()
        
        # set up GUI from designer-made layout
        self.ui = Ui_TIFgrabMW()
        self.ui.setupUi(self)

        ###                                              ###
        
        target_capdev_serialnum = capcard_short[self.sys_device]
        self.target_capdev_label = capcard_full[self.sys_device]

        print("Targeting system device ", self.sys_device)
        print("System device ",self.sys_device, "is attached to ",self.target_capdev_label)

        # Use the footprint defined in the UI to scale the captured images
        self.picframe_width=self.ui.ThumbnailView.frameGeometry().width()
        self.picframe_height=self.ui.ThumbnailView.frameGeometry().height()
        
        self.camera_device = self.sys_device.encode('utf-8')
        self.ui.Sourcename_Disp.setText(self.target_capdev_label)
        self.cam1 = QCamera(self.camera_device)
        
        # Set up behavior to capture stills
        self.cam1_capture = QCameraImageCapture(self.cam1)
        print("Still image capture from device ",self.camera_device, "capture card ",self.target_capdev_label)

        self.cam1.setCaptureMode(QCamera.CaptureStillImage)
        self.cam1_capture.setCaptureDestination(QCameraImageCapture.CaptureToBuffer)

        # Set the resolution of the capture card, which is expected to be 4K (3840x2160)
        self.cam1_imagesettings = QImageEncoderSettings()
        self.cam1_imagesettings.setResolution(self.card_res)
        self.cam1_capture.setEncodingSettings(self.cam1_imagesettings)   
        print("Cam1 has been set to resolution ", self.cam1_imagesettings.resolution())
        
        #### Assign a startup image ####
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
        self.sh = SmartHubComm()
        self.sh.new_inouts.connect(self.on_new_sh_inouts)
        self.do_smarthub_query()
        # Built in delay before invoking capture
        QTimer.singleShot(1000, self.do_capture)

    def on_timer_capture(self):
        self.sh = SmartHubComm()
        self.sh.new_inouts.connect(self.on_new_sh_inouts)
        self.do_smarthub_query()

    def do_capture(self):
        self.cam1.searchAndLock()
        self.capture_time = mysystime()
        self.capture_name = self.camera_label + "_" + self.capture_time + ".tif"
        self.cam1_capture.capture()
        self.cam1.unlock()
        
    def on_image_captured(self,id,captured_image):

        is1080 = self.check_4k_or_1080(captured_image)
        if is1080:
            captured_image = captured_image.copy(self.crop_rect)

        # The image to be displayed on screen
        self.captured2pixmap = QPixmap()
        success=self.captured2pixmap.convertFromImage(captured_image)

        self.thumb_scaled = self.captured2pixmap.scaled(self.picframe_width,self.picframe_height, Qt.KeepAspectRatio)
        self.ui.ThumbnailView.setScaledContents(True)
        self.ui.ThumbnailView.setSizePolicy(QSizePolicy.Ignored,QSizePolicy.Ignored)
        self.ui.FilenameDisp.setText(self.capture_name)
        self.ui.ThumbnailView.setPixmap(self.thumb_scaled)

        # The image to be saved to file as TIF
        # First confirm that the destination folder exists, create if it doesn't.
        self.manage_daily_folder()
        self.capture_fullpath = self.outdirname + "/" + self.capture_name
        outpixmap = QPixmap()
        outpixmap.convertFromImage(captured_image)
        outfile = QFile(self.capture_fullpath)
        outfile.open(QIODevice.WriteOnly)
        outpixmap.save(outfile, "TIFF")
        outfile.close()
        self.list_pic_stats(outpixmap)

    def check_4k_or_1080(self,myImage):
        # The capture card is set manually to a resolution of 3840x2160.
        # A 4K framegrab will fill this resolution.
        # On the Epiphan capture card a 1080 framegrab will place the image in the
        # center of this frame and put black pixels in the empty areas at the edges.
        # Examine pixels at various positions for black. If there's content everywhere
        # presume it's a 4K image. If there's content in the middle but not at edges
        # presume it's 1080. If there's no content anywhere, presume it's a dud.

        # For now check only for 1080 and not for a blank.
        
        ref_size = self.res4K   # hardcoded 4K
        pixels=[]
        if myImage.size() != self.card_res:
            print("Captured image is not ",self.card_res,"resolution")
            print("Image size is ",myImage.width(),"x",myImage.height())
            print("Operation error!!!")
            print("This code should set capture card to 3840x2160")
        else:
            myImg_assess = ImageTester(myImage)
            return myImg_assess.get_1080_status()
         
    def list_pic_stats(self, theImage):
        theSize = theImage.size()
        sizestr = ("Size:" + str(theImage.size()))
        self.ui.PicStats.setPlainText(self.sys_device)
        self.ui.PicStats.appendPlainText(sizestr)

    def do_smarthub_query(self):
        self.sh.invoke_query_of_smhub()

    def on_new_sh_inouts(self,ipl, ill, opl, oll, rtein, rteout):
        self.ill = ill
        self.rtein = rtein
        self.get_smarthub_label()
        
    def get_smarthub_label(self):
        if (self.use_smarthub == True):
            my_in_num = int(self.rtein[self.smarthub_outportnum_to_me])
            self.camera_label = self.ill[my_in_num]
            self.camera_label = remove_spaces(self.camera_label)
        # else camera_label is defined by IMAGE_PREFIX of the ini file.
        
    def on_timerradio_button(self):
        if self.ui.TimerRadio.isChecked():
            self.ui.grabButton.setEnabled(False)

            # Query the Smarthub only once for the source label
            self.sh = SmartHubComm()
            self.sh.new_inouts.connect(self.on_new_sh_inouts)
            self.do_smarthub_query()

            self.add_timer_groupbox()
        if not self.ui.TimerRadio.isChecked():
           if self.timergb:
                self.timergb.grab_timer.stop()
                self.ui.grabButton.setEnabled(True)
                self.timergb.deleteLater()
                self.timergb = None
                
    def add_timer_groupbox(self):

        self.timergb = TimerGB(75,100)

        self.timergb.grab_timeout.connect(self.do_capture)
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
        defaultlocation = "/home/data/Pictures"
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

    def do_init(self,ini_filename):
        print("Initializing params from ", ini_filename)
        cf = ConfigParser()
        cf.read(ini_filename)
        self.sh_ip=cf.get('SHUB','SHUB_IP')

        # In case proper comms with Smarthub arent working
        use_sh = cf.get('SHUB','USE_SH')
        if (use_sh == "T"):
            self.use_smarthub=True
        else:
            self.use_smarthub=False
            self.camera_label=cf.get('IMAGE','IMAGE_PREFIX')
            print("Using filename prefix from ini file is", self.camera_label)

        self.sys_device=cf.get('CAP_CARD','CAPCARD_UNIX_DEV')
        self.smarthub_outportnum_to_me = int(cf.get('SHUB','FROM_SHUB_LABEL_PORTNUM'))

        # Supports switching between capture of 3840x2160 and
        # 1920x1080 video. Note that in practice the Epiphan
        # does not scale 1:1 the image area of a 1920x1080 input.
        # Experimentally determined to be about 2740x1540, so
        # thats what used as the cropping rectangle.
        crop_rect_x = int(cf.get('IMAGE','CROP_RECT_ORIGX'))
        crop_rect_y = int(cf.get('IMAGE','CROP_RECT_ORIGY'))
        crop_rect_width = int(cf.get('IMAGE','CROP_RECT_WIDTH'))
        crop_rect_height = int(cf.get('IMAGE','CROP_RECT_HEIGHT'))
        
        self.res4K = QSize(3840,2160)
        self.res1080 = QSize(1920, 1080)
        self.card_res = self.res4K
        self.crop_rect = QRect(crop_rect_x, crop_rect_y, crop_rect_width, crop_rect_height)
        print(self.crop_rect)
        # Retained as a precaution. Uncomment as necessary.
        #self.crop_rect = QRect(555, 310, 2740, 1540);

    def manage_daily_folder(self):
        # Tests for existence of folder to hold the date's captures.
        # If folder doesn't exist, creates it.
        today = sysdate()

        self.outdirname="/data/capture_" + today
        if not os.path.exists(self.outdirname):
            os.makedirs(self.outdirname)

class ImageTester(QObject):
    # Looking for two cases
    # 1. The entire image appears black, i.e. blank.
    # 2. The edges are black, which means an image from a 1080
    #    camera is framed in the middle of this 4K image.
    #    A 1080 stream produces a 1920Wx1080H image.
    # Method:
    # Examine pixels at the edges and along a slant through the
    # middle of the field.
    # If the edges are black and the middle is not -> 1080
    # If edges and middle are black -> blank.
    #
    # Defining "black":
    # When doing computer graphics, black is RGB == 0,0,0.
    # But black pixels observed during development, as captured
    # from a Marshall V-SG4K-HDI color bar gen did not yield
    # these values. Instead, they were RGB == 13, 13, 12.
    #
    # From http://kodi.wiki/view/Video_levels_and_color_space
    # in the TV world RGB is limited range 16 - 235.
    #         < 16 is black
    #         > 235 is white.
    # So to find black look for R, G, and B all < 16.
    #
    # QPixmap origin is upper left corner.
    
    def __init__(self, image_to_examine, parent=None):
        super(ImageTester, self).__init__(parent)

        self.bk = 16
        self.is_1080 = True
        self.is_blank = True
        
        self.assess_image(image_to_examine)
        
    def assess_image(self, myImage):

        # Check for black on the edges
        xvals = [50, 50, 50, 1920, 1920, 3800, 3800]
        yvals = [50, 1080, 2110, 50, 2110, 50, 2110]

        # is_1080 has already been defined as True.
        # We just need to find one RGB component
        # of one pixel to say it's not a 1080, but instead is a 2160.
        for x, y in zip(xvals,yvals):
            myPixel = QColor(myImage.pixel(x, y))
            if (QColor.red(myPixel) >= self.bk or QColor.green(myPixel) >= self.bk or QColor.blue(myPixel) >= self.bk):
                self.is_1080 = False

        # Check for black on the diagonal
        xvals = [1000, 1920, 2840]
        yvals = [600, 1080, 1560]
        for x, y in zip(xvals,yvals):
            myPixel = QColor(myImage.pixel(x, y))
            if (QColor.red(myPixel) >= self.bk or QColor.green(myPixel) >= self.bk or QColor.blue(myPixel) >= self.bk):
                self.is_blank = False

    def get_1080_status(self):
        return(self.is_1080)

    def get_blank_status(self):
        return(self.is_blank)

def remove_spaces(instring):
    pattern = re.compile(r'\s+')
    return re.sub(pattern, '', instring)
        
if __name__ == "__main__":

    # Minor config here. User defines config filename.
    ini_filename = "tifgrab4k.ini"

    # User assigns camera label in config file.
    # Labeling is matched to an Epiphan serial number. 
    # do_init() matches label to device, e.g., "/dev/video1"
#    cam_label, cam_device = do_init(ini_filename)

    app = QApplication(sys.argv)
    
    cap_devices_full_serial, cap_devices_short_serial = get_v4l_device_list()

    gd=TIFgrabGUI(cap_devices_full_serial, cap_devices_short_serial,ini_filename)
    gd.show()
        
    sys.exit(app.exec_())
