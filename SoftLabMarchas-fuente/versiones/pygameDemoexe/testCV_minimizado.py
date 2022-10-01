#!/usr/bin/python -d
#-*- coding: utf-8 -*-

import array
import thread
import ctypes
import cv
import time, sys, os
import pykinect
from pykinect import nui
from PyQt4 import QtCore, QtGui
import win_kin

VIDEO_WINSIZE = (640,480)
"""
if hasattr(ctypes.pythonapi, 'Py_InitModule4'):
   Py_ssize_t = ctypes.c_int
elif hasattr(ctypes.pythonapi, 'Py_InitModule4_64'):
   Py_ssize_t = ctypes.c_int64
else:
   raise TypeError("Cannot determine type of Py_ssize_t")
size = Py_ssize_t()
print size 
"""

class Aplicacion(QtGui.QMainWindow):
    trigger = QtCore.pyqtSignal()
    def __init__(self, parent=None):
        super(Aplicacion, self).__init__()
        self.ui = win_kin.Ui_Form()
        self.ui.setupUi(self)
        self.frame_copy = cv.CreateImage(VIDEO_WINSIZE, cv.IPL_DEPTH_8U, 4)
        self.ipl = cv.CreateImage(VIDEO_WINSIZE, cv.IPL_DEPTH_8U, 4) # creo imagen tipo intel image procesing libray (estructura), reservo espacio .
        self.ipl_mat = array.array('c') # creo un arreglo tipo char de 1 byte cada elemento
        self.ipl_mat.fromstring(self.ipl.tostring()) # llevo ipl a cadena, y de cadena a arreglo.
        self.address = self.ipl_mat.buffer_info()[0] # buffer info= adrees y llntgh in register size
        #self.screen_lock = thread.allocate()
        self.kinect = nui.Runtime()        
        self.kinect.video_frame_ready += self.video_frame_ready
        self.kinect.video_stream.open(nui.ImageStreamType.Video, 2, nui.ImageResolution.Resolution640x480, nui.ImageType.Color)        
        self.trigger.connect(self.print_pixmap)
       
 
    def video_frame_ready(self, frame):
        #with self.screen_lock: # tomo la llave y atiendo solo este hilo.
        frame.image.copy_bits(self.address) # copio bits de frame en la dreccion adress de ipl_mat, estructura tipo ipl evidentemente.
        cv.SetData(self.ipl, self.ipl_mat.tostring()) # asigno lo que halla en ipl_mat a ipl.
        #cv.SaveImage('ipl.jpg',self.ipl)  # muestro ipl, y el buffer de la kinect se actualiza solo. :_)
        #image = QtGui.QImage(self.ipl.tostring(), self.ipl.width, self.ipl.height, QtGui.QImage.Format_RGB888).rgbSwapped()
        self.image=IplQImage(self.ipl)
        #name = QtCore.QString('Qimage.jpg')
        #self.image.save(name,"JPG");
        self.pixmap = QtGui.QPixmap.fromImage(self.image)        
        #.ui.label.setPixmap(self.pixmap)
        self.trigger.emit()

        
# hasta aca anda, pero si tengo que trabajr con mas cosas secruzan los eventos, uno locontrola pyqt y otro el kernel.      
            
    def print_pixmap(self):
        self.ui.label.setPixmap(self.pixmap)     
        
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