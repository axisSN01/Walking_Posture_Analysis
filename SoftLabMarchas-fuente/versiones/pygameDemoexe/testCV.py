#!/usr/bin/python -d
#-*- coding: utf-8 -*-

import array
import thread
import ctypes
import cv
import time

import pykinect
from pykinect import nui

get_snapshot = False
VIDEO_WINSIZE = (640,480)

if hasattr(ctypes.pythonapi, 'Py_InitModule4'):
   Py_ssize_t = ctypes.c_int
elif hasattr(ctypes.pythonapi, 'Py_InitModule4_64'):
   Py_ssize_t = ctypes.c_int64
else:
   raise TypeError("Cannot determine type of Py_ssize_t")
size = Py_ssize_t() 

def detect_and_draw(img, cascade):
    # allocate temporary images
    gray = cv.CreateImage((img.width,img.height), 8, 1)
    small_img = cv.CreateImage((cv.Round(img.width / image_scale),
                cv.Round (img.height / image_scale)), 8, 1)
    # convert color input image to grayscale
    cv.CvtColor(img, gray, cv.CV_BGR2GRAY)
    # scale input image for faster processing
    cv.Resize(gray, small_img, cv.CV_INTER_LINEAR)
    cv.EqualizeHist(small_img, small_img)
    if(cascade):
        t = cv.GetTickCount()
        faces = cv.HaarDetectObjects(small_img, cascade, cv.CreateMemStorage(0),
                                    haar_scale, min_neighbors, haar_flags, min_size)
        t = cv.GetTickCount() - t
        # print "detection time = %gms" % (t/(cv.GetTickFrequency()*1000.)), 
        if faces:
            # print "face found"
            for ((x, y, w, h), n) in faces:
                # the input to cv.HaarDetectObjects was resized, so scale the 
                # bounding box of each face and convert it to two CvPoints
                pt1 = (int(x * image_scale), int(y * image_scale))
                pt2 = (int((x + w) * image_scale), int((y + h) * image_scale))
                cv.Rectangle(img, pt1, pt2, cv.RGB(255, 0, 0), 3, 8, 0)
        else:
            # print "face not found"
            pass
        return img

def video_frame_ready(frame):
    global address, get_snapshot, frame_copy, ipl, show_face
    # print type(frame), # 
    with screen_lock:
        # array pointer to array image  
        # print type(address),
        #  pointing to an array of size: 1228800 = 640*480*4 RGBA
        # take the pointer of the array image and put it to the
        # pykinect.nui.structs.PlanarImage
        frame.image.copy_bits(address)
        # print type(frame.image), # 
        if get_snapshot:
            get_snapshot = False
            show_face = not show_face
        cv.SetData(ipl, ipl_mat.tostring())
        if show_face:
            frame_copy = detect_and_draw(ipl, cascade)
            if ipl.origin == cv.IPL_ORIGIN_TL:
                cv.Copy(ipl, frame_copy)
            else:
                cv.Flip(ipl, frame_copy, 0)
            cv.ShowImage("Kinect FaceDetect", frame_copy)
        else:
            cv.ShowImage("Kinect FaceDetect", ipl)
        
if __name__ == '__main__':
    show_face = True
    cv.NamedWindow("Kinect FaceDetect")
    cascade = cv.Load('haarcascade_frontalface_alt.xml')
    min_size = (20, 20)
    image_scale = 3
    haar_scale = 1.2
    min_neighbors = 2
    haar_flags = 0
    frame_copy = cv.CreateImage(VIDEO_WINSIZE, cv.IPL_DEPTH_8U, 4)
    ipl = cv.CreateImage(VIDEO_WINSIZE, cv.IPL_DEPTH_8U, 4)
    ipl_mat = array.array('c')
    ipl_mat.fromstring(ipl.tostring())
    # print "ipl_mat.itemsize", ipl_mat.itemsize
    # print "ipl_mat.buffer_info()", ipl_mat.buffer_info()
    # print "ipl_mat.buffer_info()[1]*ipl_mat.itemsize", ipl_mat.buffer_info()[1]*ipl_mat.itemsize
    address = ipl_mat.buffer_info()[0]
    screen_lock = thread.allocate()
    kinect = nui.Runtime()   
    kinect.video_frame_ready += video_frame_ready
    kinect.video_stream.open(nui.ImageStreamType.Video, 2, nui.ImageResolution.Resolution640x480, nui.ImageType.Color)
    print('Controls: ')
    print('     q ESC - Quit the view')
    print('     u - Increase elevation angle')
    print('     j - Decrease elevation angle')
    print('     x - set to angle == horizontal')
    print('     f - toggle facedetection')
    # main loop
    done = False
    while not done:
        k = cv.WaitKey(0)
        if k == 27: # ESC key
            done = True
            break
        elif k != -1: 
            # print k
            if k == 117: # u
                kinect.camera.elevation_angle = kinect.camera.elevation_angle + 2
            elif k == 106: # j
                kinect.camera.elevation_angle = kinect.camera.elevation_angle - 2
            elif k == 120: # x
                kinect.camera.elevation_angle = 2
            elif k == 102: # f
                get_snapshot = True
            elif k == 113: # q
                done = True
                break
    cv.DestroyWindow("Kinect FaceDetect")