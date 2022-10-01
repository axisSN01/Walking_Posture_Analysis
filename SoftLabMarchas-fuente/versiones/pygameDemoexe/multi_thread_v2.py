#!/usr/bin/python -d
# -*- coding: utf-8 -*-

# se intenta lograr que PyGameDemo.py se ejecute en un thread y win_kin.py en otro, con thread
# hay que lograr usar thread con pyqt4, que usen el mismo frame, y que puedan ahcer locks.

import array
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
                 
class cv_thread(threading.Thread):
    def __init__(self):
        super(cv_thread, self).__init__()
        self.frame_copy = cv.CreateImage(VIDEO_WINSIZE, cv.IPL_DEPTH_8U, 4)
        self.ipl = cv.CreateImage(VIDEO_WINSIZE, cv.IPL_DEPTH_8U, 4) # creo imagen tipo intel image procesing libray (estructura), reservo espacio .
        self.ipl_mat = array.array('c') # creo un arreglo tipo char de 1 byte cada elemento
        self.ipl_mat.fromstring(self.ipl.tostring()) # llevo ipl a cadena, y de cadena a arreglo.
        self.address = self.ipl_mat.buffer_info()[0] # buffer info= adrees y llntgh in register size
        
    def run(self):
        global dic
#---------------------------------------------------------------     
        def video_frame_ready(frame):
            threadLock.acquire()
            print "thread locked by cv"
            frame.image.copy_bits(self.address) # copio bits de frame en la dreccion adress de ipl_mat, estructura tipo ipl evidentemente.
            cv.SetData(self.ipl, self.ipl_mat.tostring()) # asigno lo que halla en ipl_mat a ipl.
            self.image=IplQImage(self.ipl)
            self.pixmap = QtGui.QPixmap.fromImage(self.image)        
            dic["pixmap"]=self.pixmap
            cv.ShowImage("Kinect FaceDetect", self.ipl)
            print "thread realease by cv"
            threadLock.release()
#---------------------------------------------------------------             
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
 #---------------------------------------------------------------                
            
        cv.NamedWindow("Kinect FaceDetect")
        threadLock.acquire()
        self.kinect = nui.Runtime() 
        self.kinect.video_frame_ready += video_frame_ready
        self.kinect.video_stream.open(nui.ImageStreamType.Video, 2, nui.ImageResolution.Resolution640x480, nui.ImageType.Color)
        threadLock.release()
        print('Controls: ')
        print('     q ESC - Quit the view')
        print('     u - Increase elevation angle')
        print('     j - Decrease elevation angle')
        print('     x - set to angle == horizontal')
        done = False
        while not done:
            time.sleep(0)
            k = cv.WaitKey(0)
            if k == 27: # ESC key
                done = True
                break
            elif k != -1: 
                # print k
                if k == 117: # u
                    self.kinect.camera.elevation_angle = self.kinect.camera.elevation_angle + 2
                elif k == 106: # j
                    self.kinect.camera.elevation_angle = self.kinect.camera.elevation_angle - 2
                elif k == 120: # x
                    self.kinect.camera.elevation_angle = 2
                elif k == 113: # q
                    done = True
                    break
        cv.DestroyWindow("Kinect FaceDetect")
                             
class pyqt_thread(threading.Thread):
    def __init__(self):
        super(pyqt_thread, self).__init__()
        
    def run(self):
        global dic
        class Aplicacion(QtGui.QMainWindow):
            def __init__(self):
                super(QtGui.QMainWindow, self).__init__()
                self.ui = win_kin.Ui_Form()
                self.ui.setupUi(self)
                self.timer = QtCore.QTimer(self)
                self.timer.timeout.connect(self.mostrar)        
                self.timer.start(30) 
                
            def mostrar(self):
                self.timer.stop()
                threadLock.acquire()
                print "thread locked by qt"
                if dic["pixmap"]:
                    self.ui.label.setPixmap(dic["pixmap"])
                print "thread realease by qt"
                threadLock.release()
                self.timer.start(30)

        
        app = QtGui.QApplication(sys.argv)
        app.setStyle("plastique")
        a = Aplicacion()
        a.show()
        sys.exit(app.exec_())
                   
if __name__ == '__main__':
    threadLock = threading.Lock()
    t1 = cv_thread()
    t2 = pyqt_thread()
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    
    
