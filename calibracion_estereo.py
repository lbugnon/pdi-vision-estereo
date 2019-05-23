#!/usr/bin/python
# -*- coding: latin-1 -*-
import ipdb,pickle,os
import cv2 as cv
import numpy as np
import ipdb


par_dir="camera_params/"

puntosl=pickle.load(open("%spuntos_izq.pk" %par_dir,"r"))
puntosr=pickle.load(open("%spuntos_der.pk" %par_dir,"r"))

img_shape=cv.imread("patrones/patron0_0.png",0).shape
  
objpoints=pickle.load(open("%sobjpoints.pk" %par_dir,"r"))

calc_individual=True
matrices_file="%smatrices_%s.pk" %(par_dir,"%s")

errores=[]

if calc_individual:
    # Matrices intrinsecas y de distorsión individuales
    err, Ml, Dl, rl, tl = cv.calibrateCamera(objpoints, puntosl,img_shape,None,None)
    print(Ml)
    Ml, roi_l=cv.getOptimalNewCameraMatrix(Ml,Dl,img_shape,1,img_shape)
    print(Ml)
    
    pickle.dump([err, Ml, Dl, rl, tl,roi_l],open(matrices_file %"izq","wb"))
    print(err)
    errores.append(err)
    
    err, Mr, Dr, rr, tr = cv.calibrateCamera(objpoints, puntosr,img_shape,None,None)
    print(err)
    Mr, roi_r=cv.getOptimalNewCameraMatrix(Mr,Dr,img_shape,1,img_shape)
    
    print("Ml")
    print(Ml)
    print("Mr")
    print(Mr)
    print("Dl")
    print(Dl)
    print("Dr")
    print(Dr)

    pickle.dump([err, Mr, Dr, rr, tr,roi_r],open(matrices_file %"der","wb"))
else:
    err, Ml, Dl, rl, tl,roi_l=pickle.load(open(matrices_file %"izq","br"))
    errores.append(err)
    err, Mr, Dr, rr, tr,roi_r=pickle.load(open(matrices_file %"der","br"))
    errores.append(err)

    
# Calibracion estereo
print(Ml)
err,Ml2,Dl2,Mr2,Dr2,R,T,E,F=cv.stereoCalibrate(
        objpoints, puntosl,
        puntosr, Ml, Dl, Mr,
        Dr, img_shape)
errores.append(err)
print(Ml2)

print(err)
print("R")
print(R)
print("T")
print(T)


# Rectificacion y generacion de mapas para revertir las distorsiones (directamente sobre el par estereo)
rectification_l, rectification_r, projection_l,projection_r, disparityToDepthMap, ROI_l, ROI_r = cv.stereoRectify(
        Ml2, Dl2, Mr2, Dr2, img_shape, R, T,
        None, None, None, None, None,
        0,#cv.CALIB_ZERO_DISPARITY,                  # principal points of each camera have the same pixel coordinates in rect views
        alpha=-1,
    newImageSize=img_shape)                                   # alpha=1 no pixels lost, alpha=0 pixels lost

leftMapX, leftMapY = cv.initUndistortRectifyMap(
    Ml2, Dl2, rectification_l, projection_l,
    img_shape, cv.CV_16SC2) # cv.CV_32FC1)
rightMapX, rightMapY = cv.initUndistortRectifyMap(
    Mr2, Dr2, rectification_r, projection_r,
    img_shape, cv.CV_16SC2) # cv.CV_32FC1)


pickle.dump((leftMapX,leftMapY,rightMapX,rightMapY,Ml2,Dl2,Mr2,Dr2,R,T),open("%smapping.pk" %par_dir,"wb"))
with open("%serrores_estimacion.log" %par_dir,"w") as flog:
    flog.write("%s" %errores)
