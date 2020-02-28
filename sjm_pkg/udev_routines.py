#!/usr/bin/env python3

import pyudev

def get_v4l_device_list():

    mydevs_full = {}
    mydevs_short = {}
    
    v4l_context = pyudev.Context() 
    for v4ldev in v4l_context.list_devices(subsystem='video4linux'):
        # mydevs[(v4ldev['DEVNAME'],'devname')]= v4ldev
        # mydevs[(v4ldev['DEVNAME'],'serial')]=v4ldev['ID_SERIAL']
        # mydevs[(v4ldev['DEVNAME'],'serial_short')]=v4ldev['ID_SERIAL_SHORT']
        mydevs_full[v4ldev['DEVNAME']] = v4ldev['ID_SERIAL']
        mydevs_short[v4ldev['DEVNAME']] = v4ldev['ID_SERIAL_SHORT']

    return mydevs_full, mydevs_short


##### Magewell
#P: /devices/pci0000:00/0000:00:14.0/usb3/3-1/3-1:1.0/video4linux/video0
#N: video0
#S: v4l/by-id/usb-Magewell_USB_Capture_HDMI_4K+_C209190423157-video-index0
#S: v4l/by-path/pci-0000:00:14.0-usb-0:1:1.0-video-index0
#E: COLORD_DEVICE=1
#E: COLORD_KIND=camera
#E: DEVLINKS=/dev/v4l/by-path/pci-0000:00:14.0-usb-0:1:1.0-video-index0 /dev/v4l#/by-id/usb-Magewell_USB_Capture_HDMI_4K+_C209190423157-video-index0
#E: DEVNAME=/dev/video0
#E: DEVPATH=/devices/pci0000:00/0000:00:14.0/usb3/3-1/3-1:1.0/video4linux/video0
#E: ID_BUS=usb
#E: ID_FOR_SEAT=video4linux-pci-0000_00_14_0-usb-0_1_1_0
#E: ID_MODEL=USB_Capture_HDMI_4K+
#E: ID_MODEL_ENC=USB\x20Capture\x20HDMI\x204K+
#E: ID_MODEL_ID=0009
#E: ID_PATH=pci-0000:00:14.0-usb-0:1:1.0
#E: ID_PATH_TAG=pci-0000_00_14_0-usb-0_1_1_0
#E: ID_REVISION=209f
#E: ID_SERIAL=Magewell_USB_Capture_HDMI_4K+_C209190423157
#E: ID_SERIAL_SHORT=C209190423157
#E: ID_TYPE=video
#E: ID_USB_DRIVER=uvcvideo
#E: ID_USB_INTERFACES=:0e0100:0e0200:010100:010200:030000:
#E: ID_USB_INTERFACE_NUM=00
#E: ID_V4L_CAPABILITIES=:capture:
#E: ID_V4L_PRODUCT=USB Capture HDMI 4K+: USB Captu
#E: ID_V4L_VERSION=2
#E: ID_VENDOR=Magewell
#E: ID_VENDOR_ENC=Magewell
#E: ID_VENDOR_ID=2935
#E: MAJOR=81
#E: MINOR=0
#E: SUBSYSTEM=video4linux
#E: TAGS=:uaccess:seat:
#E: USEC_INITIALIZED=155773019


### Epiphan
# P: /devices/pci0000:00/0000:00:14.0/usb3/3-2/3-2:1.1/video4linux/video1
# N: video1
# S: v4l/by-id/usb-Epiphan_Systems_Inc._AV.io_4k_HD_Video_500394-video-index0
# S: v4l/by-path/pci-0000:00:14.0-usb-0:2:1.1-video-index0
# E: COLORD_DEVICE=1
# E: COLORD_KIND=camera
# E: DEVLINKS=/dev/v4l/by-path/pci-0000:00:14.0-usb-0:2:1.1-video-index0 /dev/v4l/by-id/usb-Epiphan_Systems_Inc._AV.io_4k_HD_Video_500394-video-index0
# E: DEVNAME=/dev/video1
# E: DEVPATH=/devices/pci0000:00/0000:00:14.0/usb3/3-2/3-2:1.1/video4linux/video1
# E: ID_BUS=usb
# E: ID_FOR_SEAT=video4linux-pci-0000_00_14_0-usb-0_2_1_1
# E: ID_MODEL=AV.io_4k_HD_Video
# E: ID_MODEL_ENC=AV.io\x204k\x20HD\x20Video
# E: ID_MODEL_ID=3641
# E: ID_PATH=pci-0000:00:14.0-usb-0:2:1.1
# E: ID_PATH_TAG=pci-0000_00_14_0-usb-0_2_1_1
# E: ID_REVISION=0000
# E: ID_SERIAL=Epiphan_Systems_Inc._AV.io_4k_HD_Video_500394
# E: ID_SERIAL_SHORT=500394
# E: ID_TYPE=video
# E: ID_USB_DRIVER=uvcvideo
# E: ID_USB_INTERFACES=:ff0000:0e0100:0e0200:
# E: ID_USB_INTERFACE_NUM=01
# E: ID_V4L_CAPABILITIES=:capture:
# E: ID_V4L_PRODUCT=AV.io 4k HD Video: AV.io 4k HD
# E: ID_V4L_VERSION=2
# E: ID_VENDOR=Epiphan_Systems_Inc.
# E: ID_VENDOR_ENC=Epiphan\x20Systems\x20Inc.
# E: ID_VENDOR_ID=2b77
# E: MAJOR=81
# E: MINOR=1
# E: SUBSYSTEM=video4linux
# E: TAGS=:uaccess:seat:
# E: USEC_INITIALIZED=264647936836
