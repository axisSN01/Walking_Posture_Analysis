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
 
                 
class cv_thread(threading.Thread):
    def __init__(self):
        super(cv_thread, self).__init__()
        self.frame_copy = cv.CreateImage(VIDEO_WINSIZE, cv.IPL_DEPTH_8U, 4)
        self.ipl = cv.CreateImage(VIDEO_WINSIZE, cv.IPL_DEPTH_8U, 4) # creo imagen tipo intel image procesing libray (estructura), reservo espacio .
        self.ipl_mat = array.array('c') # creo un arreglo tipo char de 1 byte cada elemento
        self.ipl_mat.fromstring(self.ipl.tostring()) # llevo ipl a cadena, y de cadena a arreglo.
        self.address = self.ipl_mat.buffer_info()[0] # buffer info= adrees y llntgh in register size
        
    def run(self):
        def video_frame_ready(frame):
            threadLock.acquire()
            print "thread locked by cv"
            frame.image.copy_bits(self.address) # copio bits de frame en la dreccion adress de ipl_mat, estructura tipo ipl evidentemente.
            cv.SetData(self.ipl, self.ipl_mat.tostring()) # asigno lo que halla en ipl_mat a ipl.
            cv.ShowImage("Kinect FaceDetect", self.ipl)
            print "thread realease by cv"
            threadLock.release()
            
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
    
        class Aplicacion(QtGui.QMainWindow):
            def __init__(self):
                super(QtGui.QMainWindow, self).__init__()
                self.ui = win_kin.Ui_Form()
                self.ui.setupUi(self)
                self.timer = QtCore.QTimer(self)
                self.timer.timeout.connect(self.mostrar)        
                self.timer.start(30) 
                
            def mostrar(self):
                global threadLock
                self.timer.stop()
                time.sleep(0)
                threadLock.acquire()
                print "thread locked by qt"
                time.sleep(0.001)                
                #self.ui.label.setPixmap(dic["pixmap"])
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
    
    
