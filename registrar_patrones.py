#!/usr/bin/python
# -*- coding: latin-1 -*-
import cv2 as cv
import numpy as np
import ipdb
import shutil,os
import pickle
from matplotlib import pyplot as plt
import time
# Registrar N imagenes de tablero, encontrar los puntos caracteristicos

shape=(7,10)
N=120

objp = np.zeros((shape[0]*shape[1],3), np.float32)
objp[:,:2] = np.mgrid[0:shape[0],0:shape[1]].T.reshape(-1,2)
objpoints = [objp for n in range(N)] # 3d point in real world space

criteria=(cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)

imgpoints_izq = [] # 2d points in image plane.
imgpoints_der = []
nok=0

n=0
k=0
K=5

shutil.rmtree("camera_params",ignore_errors=True)
os.mkdir("camera_params")
shutil.rmtree("patrones",ignore_errors=True)
os.mkdir("patrones")
cam=[cv.VideoCapture(1),cv.VideoCapture(0)] # TODO: se podran escanear dispositivos¿?

while nok<N:
    stereo_ok=[0,0]
    ims=[[],[]]
    stereo_corners=[[],[]]
    print("%d %d" %(n,nok))
    
    # grab "congela" el frame para luego hacer la lectura. De esta forma se capturan las dos camaras prácticamente en el mismo instante de tiempo
    cam[0].grab()
    cam[1].grab()

    
    if k>=K:
        k=0
        _,im0=cam[0].retrieve() # read=grab+retrieve
        _,im1=cam[1].retrieve() 
        ims=[im0,im1]

        img=[[],[]]
        for s in [0,1]:
            ims[s]=cv.cvtColor(ims[s],cv.COLOR_BGR2GRAY)

            ret,corners=cv.findChessboardCorners(ims[s],shape)
            # Refinado de la posicion de cada esquina (se usan los gradientes de los cuadrados del patron para ajustar la estimacion inicial)
            if ret:
            
                corners=cv.cornerSubPix(ims[s],corners,winSize=(10,10),zeroZone=(-1,-1),criteria=criteria)
            
                stereo_corners[s]=corners
                
                stereo_ok[s]=1

                img[s] = cv.drawChessboardCorners(cv.cvtColor(ims[s],cv.COLOR_GRAY2BGR), shape,corners,ret)[::2,::2,:]
                
            else:
                img[s]=cv.cvtColor(ims[s][::2,::2],cv.COLOR_GRAY2BGR)

        cv.imshow("images",np.concatenate((img[0],img[1]),axis=1))
        if stereo_ok[0]==1 and stereo_ok[1]==1: # si se encuentra el patorn en ambas camaras
            imgpoints_izq.append(stereo_corners[0])
            imgpoints_der.append(stereo_corners[1])
            cv.imwrite("patrones/patron%d_0.png" %(nok),ims[0])
            cv.imwrite("patrones/patron%d_1.png" %(nok),ims[1])
            nok+=1
        n+=1
    cv.waitKey(1)
    k+=1
        
    
pickle.dump(imgpoints_izq,open("camera_params/puntos_izq.pk","wb"))
pickle.dump(imgpoints_der,open("camera_params/puntos_der.pk","wb"))
pickle.dump(objpoints,open("camera_params/objpoints.pk","wb"))

cam[0].release()
cam[1].release()
            
