#!/usr/bin/python
# -*- coding: latin-1 -*-
import cv2 as cv
import ipdb,pickle
import numpy as np
from stereo_cam import StereoCam
from stereo_match import StereoMatch
from nxt_control import NXTControl
import time,traceback
from control_panel import ControlPanel
    
# Re-mapping parameters taken from camera calibration 
mapx=[[],[]]
mapy=[[],[]]
mapx[0],mapy[0],mapx[1],mapy[1],_,_,_,_,_,_=pickle.load(open("camera_params/mapping.pk","rb"))

# Stereo-matching method: Block-Match or Semi-Global Block-Match
method=["BM","SGBM"][0]

print("Start initialization")
try: 
    # Stereo camera (independent thread)
    stereo_cam=StereoCam().start()

    # NXT LEGO control (independent thread)
    nxt=NXTControl()
    nxt_found=nxt.connect()

    # Disparity map estimation
    stereo=StereoMatch(method)

    # Stereo configurations
    control_panel=ControlPanel(stereo.get_params())

except Exception:
    print("Error in initialization")
    print(traceback.format_exc())
    
h,w=0,0

print("Start main loop. Exit with 'q'")
try: 
    while 1:
        start_time=time.time()

        im=stereo_cam.read()
        if type(im[0])==list:
            continue # waiting for the first image

        if h==0:
            h,w,c=im[0].shape

    
        cv.imshow("originales",np.concatenate((im[0][::2,::2,:],im[1][::2,::2,:]),axis=1))

        # # Ej 3 =========== 
        for s in range(2):
            # RGB to Gray scale and remap using deformation and rotation parameters 
            im[s]=cv.cvtColor(im[s],cv.COLOR_BGR2GRAY)
            im[s] = cv.remap(im[s], mapx[s], mapy[s],cv.INTER_LINEAR)
            im[s]=im[s][:h,:] # Remove zone with zeros

        # Draw horizontal lines
        for s in range(2):
            for l in range(0,500,50):
                im[s][l,:]=255
        #cv.imshow("im_mapped%d" %s ,np.concatenate((im[0][::2,::2],im[1][::2,::2]),axis=1))
        # # Ej 3 ===========


        # Ej 4-5 ===========
        params=control_panel.get_params()
        stereo.set_params(params)
        disparity = stereo.compute(im[0],im[1])
        # Ej 4-5 ===========
        
        
        # Ej 6  ==========
        # ....
        # Ej 6  ==========


        # Ej 8  ==========
        # ....
        # Ej 8  ==========

        # Ej 4 =====
        disparity=cv.putText(disparity,"FPS %.2f" %(1/(time.time()-start_time)),(10,50), cv.FONT_HERSHEY_SIMPLEX, 1,(255,255,255),2)        
        #cv.imshow("Disparidad" ,disparity)
        # Ej 4 =====
        
        key=cv.waitKey(1)
        # Manual control and possible states examples
        if nxt_found:
            if key == ord('w') or key == ord('\n'):
                nxt.set_state("move_forward")
            if key == ord('a'):
                nxt.set_state("turn_left")
            if key == ord('d'):
                nxt.set_state("turn_right")
            if key == ord('e'):
                nxt.set_state("do_nothing")
            if key == ord('x'):
                nxt.set_state("move_backwards")
                
    
        if key == ord('q'):
            print("Exit")
            break
        
except Exception:
    print("Error in the main loop")
    print(traceback.format_exc())

stereo_cam.stop()
nxt.disconnect()
