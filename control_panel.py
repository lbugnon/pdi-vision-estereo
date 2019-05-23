#!/usr/bin/python
# -*- coding: latin-1 -*-
import cv2 as cv
class ControlPanel():

    def __init__(self,params):

        cv.namedWindow("Panel",cv.WINDOW_NORMAL)
        self.params=params
        for p in sorted(params.keys()):
            cv.createTrackbar(p,"Panel",params[p][0],params[p][1],self.nothing) 
 
        
    # Creación de ventana y controles, seteo de valores por defecto
    def nothing(self,a):
        # Función para manejo de eventos, en este caso no necesitamos (solo capturamos valores)
        return

    def get_params(self):

        for p in self.params.keys():
            self.params[p][0]=cv.getTrackbarPos(p,"Panel")

        return self.params
    
