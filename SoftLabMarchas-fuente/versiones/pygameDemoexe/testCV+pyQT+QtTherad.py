#!/usr/bin/python -d
#-*- coding: utf-8 -*-
# est efue el ultimo intento con python y la kinect
import array
#import thread
import threading
import ctypes
import cv
import time, sys, os
import pykinect
from pykinect import nui
from PyQt4 import QtCore, QtGui
import win_kin

VIDEO_WINSIZE = (640,480)

  
dic={"pixmap":[]} 
          
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

        
class kin_thread(QtCore.QThread):
    def __init__(self,threadLock):
        global dic
        super(kin_thread, self).__init__()
        self.frame_copy = cv.CreateImage(VIDEO_WINSIZE, cv.IPL_DEPTH_8U, 4)
        self.ipl = cv.CreateImage(VIDEO_WINSIZE, cv.IPL_DEPTH_8U, 4) # creo imagen tipo intel image procesing libray (estructura), reservo espacio .
        self.ipl_mat = array.array('c') # creo un arreglo tipo char de 1 byte cada elemento
        self.ipl_mat.fromstring(self.ipl.tostring()) # llevo ipl a cadena, y de cadena a arreglo.
        self.address = self.ipl_mat.buffer_info()[0] # buffer info= adrees y llntgh in register size
        self.kinect = nui.Runtime()   
        self.threadLock=threadLock   
        #self.screen_lock=screen_lock

    def run(self):
        self.kinect.video_frame_ready += self.video_frame_ready
        self.kinect.video_stream.open(nui.ImageStreamType.Video, 2, nui.ImageResolution.Resolution640x480, nui.ImageType.Color)
        while True: 
            pass
                             
    def video_frame_ready(self, frame):
        threadLock.acquire()
        frame.image.copy_bits(self.address) # copio bits de frame en la dreccion adress de ipl_mat, estructura tipo ipl evidentemente.
        cv.SetData(self.ipl, self.ipl_mat.tostring()) # asigno lo que halla en ipl_mat a ipl.
        #cv.SaveImage('ipl.jpg',self.ipl)  # muestro ipl, y el buffer de la kinect se actualiza solo. :_)
        #image = QtGui.QImage(self.ipl.tostring(), self.ipl.width, self.ipl.height, QtGui.QImage.Format_RGB888).rgbSwapped()
        self.image=IplQImage(self.ipl)
        #name = QtCore.QString('Qimage.jpg')
        #self.image.save(name,"JPG");
        self.pixmap = QtGui.QPixmap.fromImage(self.image)        
        dic["pixmap"]=self.pixmap
        threadLock.release()
        
        
class pyqt_thread(threading.Thread):
    def __init__(self):
        super(pyqt_thread, self).__init__()
        self.app = QtGui.QApplication(sys.argv)
        self.app.setStyle("plastique")
        
        
    def run(self):
        a = self.Aplicacion()
        a.show()
        sys.exit(self.app.exec_())
        
    class Aplicacion(QtGui.QMainWindow):
        def __init__(self):
            super(QtGui.QMainWindow, self).__init__()
            self.ui = win_kin.Ui_Form()
            self.ui.setupUi(self)
            self.timer = QtCore.QTimer(self)
            self.timer.timeout.connect(self.mostrar)        
            self.timer.start(2000)
            
        def mostrar(self):
            self.timer.stop()
            #self.ui.label.setPixmap(dic["pixmap"])
            print "pyqt_thread"
            self.timer.start(2000)   
        
if __name__ == '__main__':
    threadLock = threading.Lock()
    #t1 = kin_thread(threadLock)
    t2 = pyqt_thread()
    #t1.start()
    #t1.run()
    t2.start()
    t2.run()   
