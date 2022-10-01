#!/usr/bin/python -d
# -*- coding: utf-8 -*-

# sintoma, falla MSVCR90.dll, puede ser por el driver de pykinect (9.0.30729.6161), el problema era el timer de CV.WaitKey;
# pygmael o que hace es, en el evento de video dibuja esqueleto si esta habilitado, yademas tiene un evento solo para skeleto(pero sin LOCK)
import array
import threading
import ctypes
import cv
import time, sys, os
import pykinect
from pykinect import nui
from pykinect.nui import JointId
from PyQt4 import QtCore, QtGui
import win_kin
import itertools

#----------------parametros-----------------------------------------------
VIDEO_WINSIZE = (640,480)

LEFT_ARM = (JointId.ShoulderCenter, 
            JointId.ShoulderLeft, 
            JointId.ElbowLeft, 
            JointId.WristLeft, 
            JointId.HandLeft)
RIGHT_ARM = (JointId.ShoulderCenter, 
             JointId.ShoulderRight, 
             JointId.ElbowRight, 
             JointId.WristRight, 
             JointId.HandRight)
LEFT_LEG = (JointId.HipCenter, 
            JointId.HipLeft, 
            JointId.KneeLeft, 
            JointId.AnkleLeft, 
            JointId.FootLeft)
RIGHT_LEG = (JointId.HipCenter, 
             JointId.HipRight, 
             JointId.KneeRight, 
             JointId.AnkleRight, 
             JointId.FootRight)
SPINE = (JointId.HipCenter, 
         JointId.Spine, 
         JointId.ShoulderCenter, 
         JointId.Head)
dic={"pixmap":[]}
frame_skeleton=pykinect.nui.structs.SkeletonFrame() # estructura de dato esqueleto,sacado de structs.py
is_sk=False
#--------------------------------------------------------------- 
        
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
        global frame_skeleton
        global is_sk
#---------------------------------------------------------------     
        def video_frame_ready(frame):
            global frame_skeleton, is_sk
            threadLock.acquire()
            frame.image.copy_bits(self.address) # copio bits de frame en la dreccion adress de ipl_mat, estructura tipo ipl evidentemente.
            cv.SetData(self.ipl, self.ipl_mat.tostring()) # asigno lo que halla en ipl_mat a ipl.
            try:
                if is_sk:
                    for index, data in enumerate(frame_skeleton.SkeletonData):
                    # draw the Head
                        HeadPos = nui.SkeletonEngine.skeleton_to_depth_image(data.SkeletonPositions[JointId.Head], 640, 480)
                        cv.Circle(self.ipl,(int(HeadPos[0]),int(HeadPos[1])),40,[0,0,255],-1)
            except: 
                print "Unexpected error:", sys.exc_info()[0]
            self.image=IplQImage(self.ipl)
            self.pixmap = QtGui.QPixmap.fromImage(self.image)        
            dic["pixmap"]=self.pixmap
            threadLock.release()
#---------------------------------------------------------------     
        def save_skeleton(frameSk):
            global frame_skeleton, is_sk
            frame_skeleton= frameSk
            is_sk=True
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
        threadLock.acquire() # tomo el lock para el seteo
        self.kinect = nui.Runtime()
        self.kinect.skeleton_engine.enabled = True        
        self.kinect.skeleton_frame_ready += save_skeleton 
        self.kinect.video_frame_ready += video_frame_ready
        self.kinect.video_stream.open(nui.ImageStreamType.Video, 1, nui.ImageResolution.Resolution640x480, nui.ImageType.Color)
        threadLock.release()
        done = False
        while not done:
            time.sleep(0.001)
            pass

                             
class pyqt_thread(threading.Thread):
    def __init__(self):
        super(pyqt_thread, self).__init__()
        
    def run(self):
        global dic
#---------------------------------------------------------------        
        class Aplicacion(QtGui.QMainWindow):
            def __init__(self):
                super(QtGui.QMainWindow, self).__init__()
                self.ui = win_kin.Ui_Form()
                self.ui.setupUi(self)
                self.timer = QtCore.QTimer(self)
                self.timer.timeout.connect(self.mostrar)        
                self.timer.start(50) 
                
            def mostrar(self):
                self.timer.stop()
                threadLock.acquire()
                if dic["pixmap"]:
                    self.ui.label.setPixmap(dic["pixmap"])
                threadLock.release()
                self.timer.start(50)
#---------------------------------------------------------------        
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
    
    
"""       def draw_skeletons(frame):
            threadLock.acquire()
            if dic["pixmap"] != None:
                try:
                    #frame.image.copy_bits(self.address) # copio bits de frame en la dreccion adress de ipl_mat, estructura tipo ipl.
                    #cv.SetData(self.ipl, self.ipl_mat.tostring()) # asigno lo que halla en ipl_mat a ipl.
                    for index, data in enumerate(frame.SkeletonData):
                        # draw the Head
                        HeadPos = nui.SkeletonEngine.skeleton_to_depth_image(data.SkeletonPositions[JointId.Head], 640, 480) 
                        cv.Circle(self.ipl,(int(HeadPos[0]), int(HeadPos[1])),4,[0,255,0],-1)
                        print "dibuje cabeza"                        
                        # drawing the the whole body
                        #draw_skeleton_data(data, index, SPINE, 10)
                        #draw_skeleton_data(data, index, LEFT_ARM)
                        #draw_skeleton_data(data, index, RIGHT_ARM)
                        #draw_skeleton_data(data, index, LEFT_LEG)
                        #draw_skeleton_data(data, index, RIGHT_LEG)
                    cv.SetData(self.ipl, self.ipl_mat.tostring())
                    self.image=IplQImage(self.ipl)
                    self.pixmap = QtGui.QPixmap.fromImage(self.image)        
                    dic["pixmap"]=self.pixmap
                except: pass
            threadLock.release()           
#---------------------------------------------------------------
        def draw_skeleton_data(pSkelton, index, positions, thickness = 2):
            start = pSkelton.SkeletonPositions[positions[0]] # stars es el indice de inicio, no es cero.
               
            for position in itertools.islice(positions, 1, None): # itertools.islice(iterador, inicio, stop, step)
                next = pSkelton.SkeletonPositions[position.value] # proximo punto del hueso en cuestion (la otra punta)
                curstart = nui.SkeletonEngine.skeleton_to_depth_image(start, 640, 480) # extrae x,y,z,w de un punto, escalado en dispInfo.
                curend = nui.SkeletonEngine.skeleton_to_depth_image(next, 640, 480)

                cv.Line(self.ipl,curstart, curend,[25,20,175], thickness=2, lineType=cv.CV_AA, shift=0)
                
                start = next"""