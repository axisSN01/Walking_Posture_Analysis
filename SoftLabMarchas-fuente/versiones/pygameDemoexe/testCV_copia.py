"""provides a simple sample with video and face detection via OpenCV and the Kinect camera"""

import array
import thread
import ctypes
import cv
import time, sys, os
import pykinect
from pykinect import nui
from PyQt4 import QtCore, QtGui
import win_kin
get_snapshot = False
VIDEO_WINSIZE = (640,480)

#------------------------------------------------------------------------
if hasattr(ctypes.pythonapi, 'Py_InitModule4'):
   Py_ssize_t = ctypes.c_int
elif hasattr(ctypes.pythonapi, 'Py_InitModule4_64'):
   Py_ssize_t = ctypes.c_int64
else:
   raise TypeError("Cannot determine type of Py_ssize_t")
size = Py_ssize_t() 
#------------------------------------------------------------------------

class Aplicacion(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = win_kin.Ui_Form()
        self.ui.setupUi(self)
        frame_copy = cv.CreateImage(VIDEO_WINSIZE, cv.IPL_DEPTH_8U, 4)
        ipl = cv.CreateImage(VIDEO_WINSIZE, cv.IPL_DEPTH_8U, 4)
        ipl_mat = array.array('c')
        ipl_mat.fromstring(ipl.tostring())
        address = ipl_mat.buffer_info()[0]
        screen_lock = thread.allocate()
        kinect = nui.Runtime()   
        kinect.video_frame_ready += self.video_frame_ready
        kinect.video_stream.open(nui.ImageStreamType.Video, 2, nui.ImageResolution.Resolution640x480, nui.ImageType.Color)
#------------------------------------------------------------------------------- 
    def video_frame_ready(self, frame):
        # print type(frame), # 
        with screen_lock:
            # array pointer to array image  
            # print type(address),
            #  pointing to an array of size: 1228800 = 640*480*4 RGBA
            # take the pointer of the array image and put it to the
            # pykinect.nui.structs.PlanarImage
            frame.image.copy_bits(address)
            # print type(frame.image), # 
            cv.SetData(ipl, ipl_mat.tostring())
            Qframe=IplQImage(ipl)
            self.ui.label.setPixmap(QtGui.QPixmap.fromImage(Qframe))             
        

class IplQImage(QtGui.QImage):
    """ Clase para conversion de iplimages a qimages """
    def __init__(self,iplimage):
        alpha = cv.CreateMat(iplimage.height,iplimage.width, cv.CV_8UC1)
        cv.Rectangle(alpha, (0, 0), (iplimage.width,iplimage.height), cv.ScalarAll(255) ,-1)
        rgba = cv.CreateMat(iplimage.height, iplimage.width, cv.CV_8UC4)
        cv.Set(rgba, (1, 2, 3, 4))
        cv.MixChannels([iplimage, alpha],[rgba], [
        (0, 0), # rgba[0] -> bgr[2]
        (1, 1), # rgba[1] -> bgr[1]
        (2, 2), # rgba[2] -> bgr[0]
        (3, 3)  # rgba[3] -> alpha[0]
        ])
        self.__imagedata = rgba.tostring()
        super(IplQImage,self).__init__(self.__imagedata, iplimage.width, iplimage.height, QtGui.QImage.Format_RGB32)
        
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    app.setStyle("plastique")
    a = Aplicacion()
    a.show()
    sys.exit(app.exec_())

