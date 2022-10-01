#!/usr/bin/python -d
# -*- coding: utf-8 -*-

import array, numpy
import threading
import ctypes
import cv
import time, sys, os, glob
import pykinect
from pykinect import nui
from pykinect.nui import JointId
from PyQt4 import QtCore, QtGui, phonon
import itertools
from curvas import Ui_curvas
from videoPlayer import Ui_video
from ventana1 import Ui_ventana
import numpy as np
from scipy import stats
import subprocess
#----------------parametros-----------------------------------------------
VIDEO_WINSIZE = (640,480)
Nframes=140
TOBILLOS_IZ_PX_LIST=range(0,Nframes) 
TOBILLOS_DE_PX_LIST=range(0,Nframes) 
TOBILLOS_IZ_LIST=range(0,Nframes) 
TOBILLOS_DE_LIST=range(0,Nframes)
TOBILLO_IZ=range(0,3)
TOBILLO_DE=range(0,3)
TOBILLO_IZ_PX=range(0,2)
TOBILLO_DE_PX=range(0,2)
DISTANCIA=range(0,Nframes)
TIEMPO=range(0,Nframes)
DMAX=0.0
DMIN=0.0
IMAX=0
IMIN=0
IPL_LIST=range(0,Nframes)       
for i in range(0,Nframes):
    IPL_LIST[i]=cv.CreateImage(VIDEO_WINSIZE, cv.IPL_DEPTH_8U, 4)
        
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
dic={"grabando":False,"i":0}
#---------------------------------------------------------------
class Aplicacion(QtGui.QMainWindow):
    grabar=QtCore.pyqtSignal()   
    def __init__(self, parent=None):
        super(Aplicacion, self).__init__()
        self.ui = Ui_ventana()
        self.ui.setupUi(self)
        self.center()
#------------signals and slots--------------------------------------------------- 
        self.grabar.connect(self.grabar_video)
        self.ui.tabWidget.setCurrentWidget(self.ui.tabIni)
        self.ui.actionCerrar.triggered.connect(self.close)
        self.ui.bot_conf.clicked.connect(self.ir_conf)
        self.ui.bot_curvas.clicked.connect(self.ver_curvas)
        self.ui.bot_video.clicked.connect(self.ver_video)
        self.ui.bot_ini.clicked.connect(self.iniciar)
        #self.ui.tableView()
#------------------------Asigno variables y registros----------------------------
        global dic,VIDEO_WINSIZE,Nframes,TOBILLOS_IZ_LIST,TOBILLOS_DE_LIST,TOBILLO_IZ,TOBILLO_IZ_PX,TOBILLO_DE_PX,TOBILLO_DE,IPL_LIST,TOBILLOS_DE_PX_LIST,TOBILLOS_IZ_PX_LIST
        self.frame_copy = cv.CreateImage(VIDEO_WINSIZE, cv.IPL_DEPTH_8U, 4)
        self.ipl = cv.CreateImage(VIDEO_WINSIZE, cv.IPL_DEPTH_8U, 4) # creo imagen tipo intel image procesing libray (estructura), reservo espacio .
        ### OJO AL PARCHE, aca allocate arreglos para la parte de grabacion, puede llevar hasta 1 GB de RAM.
        self.ipl_mat= array.array('c') # creo un arreglo tipo char de 1 byte cada elemento
        self.ipl_mat.fromstring(self.ipl.tostring()) # llevo ipl a cadena, y de cadena a array
        self.address = self.ipl_mat.buffer_info()[0] # buffer info= adrees y llntgh in register size
        self.frame=[]
        self.SkFrame=[]
        self.velocidad=0.0
#---------------Inicio kinect----------------------------------------------------------------
        self.kinect = nui.Runtime()
        self.kinect.skeleton_engine.enabled = True        
        self.kinect.video_stream.open(nui.ImageStreamType.Video, 2, nui.ImageResolution.Resolution640x480, nui.ImageType.Color)
#------------------------arranco Qtimer-----------------------------------------------------        
        self.ui.label_conf_2.setText(">>>tiempo pre-configurado: 6.5seg\n")
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.mostrar)
        self.ui.consola.append(">>>Iniciando...\n")
        self.ui.consola.append(">>>tiempo pre-configurado: 6.5seg\n") 
        self.inicio=time.clock()
        self.timer.start(30)                                           
#-----------------------------------------------------------------------------
    def mostrar(self):
        global dic,VIDEO_WINSIZE,Nframes,TOBILLOS_IZ_LIST,TOBILLOS_DE_LIST,TOBILLO_IZ,TOBILLO_DE,IPL_LIST,DISTANCIA,TIEMPO,DMAX,DMIN,IMAX,IMIN
        global TOBILLO_IZ_PX,TOBILLO_DE_PX,TOBILLOS_DE_PX_LIST,TOBILLOS_IZ_PX_LIST
        self.timer.stop()
        self.frame=[]
        self.SkFrame=[]
        self.ipl = cv.CreateImage(VIDEO_WINSIZE, cv.IPL_DEPTH_8U, 4)        
        try:
            self.frame = self.kinect.video_stream.get_next_frame(3)            
            if self.frame:
                self.frame.image.copy_bits(self.address) # copio bits de frame en la dreccion adress de ipl_mat, estructura tipo ipl evidentemente.
                self.kinect._nui.NuiImageStreamReleaseFrame(self.kinect.video_stream._stream, self.frame)                                   
                cv.SetData(self.ipl, self.ipl_mat.tostring()) # asigno lo que halla en ipl_mat a ipl.                                        
        except:
            pass
            self.ui.consola.append(">>>error frame..\n")           
        try:  
            self.SkFrame = self.kinect.skeleton_engine.get_next_frame()              
            for index, data in enumerate(self.SkFrame.SkeletonData):
                if  data.eTrackingState != nui.SkeletonTrackingState.NOT_TRACKED:
                    # draw the Head
                    HeadPos = nui.SkeletonEngine.skeleton_to_depth_image(data.SkeletonPositions[JointId.Head], 640, 480)
                    cv.Circle(self.ipl,(int(HeadPos[0]),int(HeadPos[1])),20,[0,0,255],-1)
                    #guardo datos de tobillos, para cada skeleto encontrado(sobreescribo si hay varios)      
                    TOBILLO_IZ= [float(data.SkeletonPositions[LEFT_LEG[3]].x), float(data.SkeletonPositions[LEFT_LEG[3]].y), float(data.SkeletonPositions[LEFT_LEG[3]].z)]
                    TOBILLO_DE= [float(data.SkeletonPositions[RIGHT_LEG[3]].x), float(data.SkeletonPositions[RIGHT_LEG[3]].y), float(data.SkeletonPositions[RIGHT_LEG[3]].z)]               
                    #guardo datos de tobillos, en pixeles
                    TOBILLO_IZ_PX= nui.SkeletonEngine.skeleton_to_depth_image(data.SkeletonPositions[JointId.AnkleLeft], 640, 480)
                    TOBILLO_DE_PX= nui.SkeletonEngine.skeleton_to_depth_image(data.SkeletonPositions[JointId.AnkleRight], 640, 480)
                    # drawing the the whole body
                    self.draw_skeleton_data(data, index, SPINE, 10)
                    self.draw_skeleton_data(data, index, LEFT_ARM)
                    self.draw_skeleton_data(data, index, RIGHT_ARM)
                    self.draw_skeleton_data(data, index, LEFT_LEG)
                    self.draw_skeleton_data(data, index, RIGHT_LEG)
                            
        except: #pass
            self.SkFrame=[]            
            self.ui.consola.append(">>>error skeleton..\n")
        #    
        if dic["grabando"] and dic["i"]<Nframes:
            #tomo marca de tiempo del frame        
            if dic["i"]==0:
                TIEMPO[0]=time.clock()
                
            TIEMPO[dic["i"]]=round((time.clock()-TIEMPO[0]),5)
            IPL_LIST[dic["i"]]=cv.CloneImage(self.ipl)
            # grabo tobillos
            if self.SkFrame != []:# si estoy grabando y hay esqueleto, etonces guardo los tobillso de ese frame en la lista
                TOBILLOS_IZ_PX_LIST[dic["i"]]=TOBILLO_IZ_PX
                TOBILLOS_DE_PX_LIST[dic["i"]]=TOBILLO_DE_PX
                TOBILLOS_IZ_LIST[dic["i"]]=[TOBILLO_IZ[0],TOBILLO_IZ[1]] 
                TOBILLOS_DE_LIST[dic["i"]]=[TOBILLO_DE[0],TOBILLO_DE[1]]
            else: # sino ese item es cero.
                TOBILLOS_IZ_PX_LIST[dic["i"]]=[0.0,0.0]
                TOBILLOS_DE_PX_LIST[dic["i"]]=[0.0,0.0]              
                TOBILLOS_IZ_LIST[dic["i"]]=[0.0,0.0]
                TOBILLOS_DE_LIST[dic["i"]]=[0.0,0.0]
                
            self.ui.consola.append(">>>RAMING frame"+str(dic["i"])+"..\n")
            dic["i"]=dic["i"]+1  
            
        if dic["grabando"] and dic["i"]>=Nframes:
            dic["grabando"]=False
            dic["i"]=0                  
            self.grabar.emit()
            
        self.image=IplQImage(self.ipl)
        self.pixmap = QtGui.QPixmap.fromImage(self.image)
        self.ui.labelcamara.setPixmap(self.pixmap)
        self.timer.start(30)
        
#---------------------------------------------------------------
    def draw_skeleton_data(self, pSkelton, index, positions, thickness = 10):
        start = pSkelton.SkeletonPositions[positions[0]] # stars es el indice de inicio, no es cero.
        for position in itertools.islice(positions, 1, None): # itertools.islice(iterador, inicio, stop, step)
            next = pSkelton.SkeletonPositions[position.value] # proximo punto del hueso en cuestion (la otra punta)
            curstart = nui.SkeletonEngine.skeleton_to_depth_image(start, 640, 480) # extrae x,y,z,w de un punto, escalado en dispInfo.
            curend = nui.SkeletonEngine.skeleton_to_depth_image(next, 640, 480)
            cv.Line(self.ipl,(int(curstart[0]),int(curstart[1])), (int(curend[0]),int(curend[1])),[255,0,0], thickness)                
            start = next          
#-----------------------------------------------------------------------------
    def center(self):
        screen = QtGui.QDesktopWidget().screenGeometry()
        size =  self.geometry()
        self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)
#-----------------------------------------------------------------------------        
    def ir_conf(self):
        self.ui.tabWidget.setCurrentWidget(self.ui.tabConf)  # cambia tab a configuracion
#-----------------------------------------------------------------------------                
    def ver_curvas(self):
        if  self.ui.bot_curvas.isChecked():
            self.wid_curvas=curvas()          
            self.wid_curvas.show()
        if not self.ui.bot_curvas.isChecked():               
            self.wid_curvas.close()
#-----------------------------------------------------------------------------
    def ver_video(self):
        dlg=QtGui.QFileDialog()
        directory=sys.path[0]+"\\ensayos\\"
        pathVideo=dlg.getOpenFileName(self,"Abrir Video del ensayo..",directory,"Videos (*.avi *.mp4 *.mov);; All Files (*.*)")
        pathVideo=str(pathVideo)
        media = phonon.Phonon.MediaSource(pathVideo)        
        #media = phonon.Phonon.MediaSource('prueba.avi')
        if  self.ui.bot_video.isChecked():
            self.wid_video=video()
            self.wid_video.video.videoPlayer.load(media)
            self.wid_video.show()                  
            #self.wid_video.video.videoPlayer.play()
            QtCore.QObject.connect(self.wid_video ,QtCore.SIGNAL("close()"), self.wid_video.video.videoPlayer.stop)                   
        if not self.ui.bot_video.isChecked():
            #self.wid_video.video.videoPlayer.stop()
            self.wid_video.close()                 
#-----------------------------------------------------------------------------
    def iniciar(self): 
        if  self.ui.bot_ini.isChecked() and not dic["grabando"]:    
            self.timer.stop()
            #dic["iterador"]=iter(range(0,Nframes))
            dic["i"]=0
            self.ui.consola.append(">>>grabando: 8seg... \n") 
            dic["grabando"]=True
            self.timer.start(30)            
        elif  self.ui.bot_ini.isChecked() and dic["grabando"]:
            self.ui.consola.append(">>>por favor espere (grabando)... \n") 
#-----------------------------------------------------------------------------
    def grabar_video(self):
        global dic,VIDEO_WINSIZE,Nframes,TOBILLOS_IZ_LIST,TOBILLOS_DE_LIST,TOBILLO_IZ,TOBILLO_DE     
        global TOBILLOS_DE_PX_LIST,TOBILLOS_IZ_PX_LIST,TOBILLO_IZ_PX,TOBILLO_DE_PX,IPL_LIST,DISTANCIA,TIEMPO,DMAX,DMIN,IMAX,IMIN
        try:
            self.ui.consola.append(">>>aguarde por favor, procesando datos..\n")
            #------------------post-procesado de los tobillos-------------------------------------------            
     ## para armar la serie de datos de dispercion, primero, borro datos erroneos de las listas
            dispersion_tobillos=[]
            for i in range(0,Nframes):
                if TOBILLOS_IZ_LIST[i]==[0.0, 1.0] or TOBILLOS_IZ_LIST[i]==[0.0, 0.0]:
                    pass
                else:
                    dispersion_tobillos.append(TOBILLOS_IZ_LIST[i])
                    
                if TOBILLOS_DE_LIST[i]==[0.0, 1.0] or TOBILLOS_DE_LIST[i]==[0.0, 0.0]:
                    pass
                else:
                    dispersion_tobillos.append(TOBILLOS_DE_LIST[i])                
                
            dispersion_tobillos=np.array(TOBILLOS_IZ_LIST+TOBILLOS_DE_LIST)
            ## calculo regresion lineal de los datos de tobillos
            pendiente, ordenada, r_value, p_value, std_err = stats.linregress(dispersion_tobillos)
            for i in range(0,Nframes):
                if TOBILLOS_IZ_LIST[i]==[0.0, 1.0] or TOBILLOS_IZ_LIST[i]==[0.0, 0.0]:
                    DISTANCIA[i]=0
                    
                elif TOBILLOS_DE_LIST[i]==[0.0, 1.0] or TOBILLOS_DE_LIST[i]==[0.0, 0.0]:
                    DISTANCIA[i]=0
                    
                else:
                    dx=abs(TOBILLOS_IZ_LIST[i][0]-TOBILLOS_DE_LIST[i][0])
                    IZy=float(pendiente*TOBILLOS_IZ_LIST[i][0]+ordenada)
                    DEy=float(pendiente*TOBILLOS_DE_LIST[i][0]+ordenada)               
                    dy=abs(IZy-DEy) 
                    DISTANCIA[i]=round((dx+dy)**0.5,5)# ajusto a 5 decimales  
                
            DMAX=max(DISTANCIA)
            IMAX=DISTANCIA.index(DMAX)
            i=0
            j=True
            DMIN=DISTANCIA[IMAX+i]
            i1=0
            i2=0
            while j:# busco la menor distancia de paso hacia adelante
                try:
                    if DMIN>=DISTANCIA[IMAX+i]:# si la distancia[i] es menor que DMIN, entonces DMIN=distancia(i)
                        DMIN=DISTANCIA[IMAX+i]
                    else:
                        j=False
                        i1=DISTANCIA.index(DMIN) # si la distancia empieza a crecer, entonces encontre el minimo hacia adelante.
                        
                    i=i+1                        
                except IndexError:# si llego al final, tomo ese como la distancia minima. 
                    j=False
                    i1=DISTANCIA.index(DMIN)
            j=True
            i=0
            DMIN=DISTANCIA[IMAX-i]          
            while j:
                try:# busco la menor distancia de paso hacia atras
                    if DMIN>=DISTANCIA[IMAX-i] and (IMAX-i)>=0:# chequeo propiedad de las listas. indice hacia atras.
                        DMIN=DISTANCIA[IMAX-i]
                    else:
                        j=False
                        i2=DISTANCIA.index(DMIN)
                    i=i+1    
                except IndexError:
                    j=False
                    i2=DISTANCIA.index(DMIN)
                
            if DISTANCIA[i1]<=DISTANCIA[i2]:
                DMIN=DISTANCIA[i1]
                IMIN=i1
            else:    
                DMIN=DISTANCIA[i2]
                IMIN=i2

            # seteo valores de salida del post-precesado###
            self.velocidad=(DISTANCIA[IMAX]-DISTANCIA[IMIN])/abs((TIEMPO[IMAX]-TIEMPO[IMIN]))
            self.ui.label_res_1.setText("Velocidad [Mts/Seg]: "+str(round(self.velocidad,2)))
            self.ui.label_res_2.setText("Distancia de paso [Metros]: "+str(round(DMAX,2)))

            
     #------------------guardo frames, con nombre, datos,y dist max de tobillos-------------------------------------------            

            self.ui.consola.append(">>>procediendo a guardar..\n")
            nameB=self.ui.lineEdit.text()  # Qstring devuelve UNICODE, tengo que llevar a asci hay que traducirlas
            edadB=self.ui.lineEdit_2.text()
            nameB=str(nameB.toAscii())
            edadB=str(edadB.toAscii())
            nombre=b'Nombre: ' + nameB
            edad=b'Edad: '+ edadB
            fecha= time.strftime("Fecha= %d-%B-%Y_%H-%MHs")
            vel="Velocidad media [Mts/Seg]: "+str(round(self.velocidad,2))
            distancia= "Distancia de paso [Metros]: "+str(round(DMAX,2))
            tob_iz_max=TOBILLOS_IZ_PX_LIST[IMAX]
            tob_de_max=TOBILLOS_DE_PX_LIST[IMAX]
            font = cv.InitFont(5,0.7,0.7,1.0,1,8) # inicializo una fuente por si hay q escribir algo en pantalla
            for i in range(0,Nframes):
                cv.Line(IPL_LIST[i],(int(tob_iz_max[0]),int(tob_iz_max[1])), (int(tob_de_max[0]),int(tob_de_max[1])),[0,255,0], thickness=10)
                cv.PutText(IPL_LIST[i], nombre, (10,20), font, [0,0,0])
                cv.PutText(IPL_LIST[i], edad, (10,35), font, [0,0,0])
                cv.PutText(IPL_LIST[i], fecha, (10,50), font, [0,0,0])
                cv.PutText(IPL_LIST[i], vel, (10,65), font, [0,0,0])
                cv.PutText(IPL_LIST[i], distancia, (10,80), font, [0,0,0])
                
                cv.SaveImage(sys.path[0]+"/temp/Frames/ipl"+str(i)+".jpg",IPL_LIST[i])                
            self.ui.consola.append(">>>guardando en disco..\n")
     #------------------arranco treath que graba video-------------------------------------------            
            
            grab=grab_thread(nameB,fecha)
            grab.start()
            self.ui.consola.append(">>>vaya a resultados, por favor..\n")           
        except:
            self.ui.consola.append(">>>No se pudo grabar, intente de nuevo..\n")

     #------------------guardo variables en archivo CSV: tiempo, tobillos De y IZ, DISTANCIA, etc----------------
        try:
            import csv
            file=open(sys.path[0]+'/ensayos/'+nameB+fecha+'.csv','wb')
            writer=csv.writer(file,delimiter=',')
            writer.writerow(['TIEMPO_seg','TOBILLO_DERECHO_x_mts','TOBILLO_DERECHO_y_mts','TOBILLO_IZQUIERDO_x_mts','TOBILLO_IZQUIERDO_y_mts','DISTANCIA_TOBILLOS_mts'])
            for i in range(0,Nframes):                    
                writer.writerow([TIEMPO[i],TOBILLOS_DE_LIST[i][0],TOBILLOS_DE_LIST[i][0],TOBILLOS_IZ_LIST[i][1],TOBILLOS_IZ_LIST[i][1],DISTANCIA[i]])
            file.close()
            del(writer)
            del(csv)            
        except:
            self.ui.consola.append(">>>No se pudo guardar archivo CSV \n")            
          
 #-----------------------------------------------------------------------------
    def closeEvent(self,event):
        reply = QtGui.QMessageBox.question(self, 'Atención:',
            "Esta seguro de salir?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            self.kinect.close()
            print "cerrando kinect"
            self.wid_video.close() 
            self.wid_curvas.close()            
            event.accept()
        else:
            event.ignore()    
#------------objetos externos-----------------------------------------------------------------              
class curvas(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self)
        self.curvas = Ui_curvas()
        self.curvas.setupUi(self)
#---------------------------------------------------------------                    
class video(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.video = Ui_video()
        self.video.setupUi(self)                
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
                  
class grab_thread(threading.Thread):
    
    def __init__(self,nombre,fecha):
        super(grab_thread, self).__init__()
        self.nombre=nombre
        self.fecha=fecha
        self.videoName="\""+sys.path[0]+"\\ensayos\\"+nombre+" "+fecha+".avi\""
        self.frames="\""+sys.path[0]+"\\temp\\Frames\\ipl%d.jpg\""
        self.ffmpeg="\""+sys.path[0]+"\\ffmpeg\\bin\\ffmpeg.exe\""
        self.cmd=self.ffmpeg+" -y -start_number 0 -i "+self.frames+" -framerate 15 -vcodec libx264 -r 15 "+self.videoName
    def run(self):
        i=0
        try:
            subprocess.call(self.cmd)
        except:
            print "no se pudo grabar video"
 #---------------------------------------------------------------
 
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    app.setStyle("plastique")
    a = Aplicacion()
    a.show()
    sys.exit(app.exec_())
                   

    
    
