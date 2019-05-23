import cv2 as cv
import numpy as np
class StereoMatch():


    def __init__(self,method):

        self.method=method
        # param_name: actual_value,max_value (minimum is allways zero)
        self.params={"min_disp": [0,255],
                     "num_disp":  [16,255],
                     "speckle_window_size": [0,400],#100
                     "speckle_range": [0,128],
                     "uniqueness": [0,20],
                     "block_size": [5,60]
                     }

   
        
        if method=="SGBM":
            ws=3
            self.params["window_size"] = [ws,20]#3
            p1,p2=self.get_p1_p2(ws)    
            
            self.stereo = cv.StereoSGBM_create(minDisparity = self.params["min_disp"][0],
                              numDisparities = self.params["num_disp"][0],
                              blockSize = self.params["block_size"][0],
                              P1 = p1,
                              P2 = p2,
                              uniquenessRatio = self.params["uniqueness"][0],
                              speckleWindowSize = self.params["speckle_window_size"][0],
                              speckleRange = self.params["speckle_range"][0])


        if method=="BM":
            self.stereo = cv.StereoBM_create(numDisparities = self.params["num_disp"][0],
                                        blockSize = self.params["block_size"][0])
            self.stereo.setUniquenessRatio(self.params["uniqueness"][0])

            
    def get_params(self):
        return self.params

    def compute(self,iml,imr):
        
        disparity = self.stereo.compute(iml,imr)
        disparity-=np.min(disparity)
        
        return (255.0*disparity/np.max(disparity)).astype("uint8")
        #return (255.0*disparity/np.max(self.params["num_disp"][0])).astype("uint8")

    
    def set_params(self,params):

        
        self.stereo.setMinDisparity(params["min_disp"][0]) 

        nd=params["num_disp"][0] # must be divisible by 16
        nd-=nd%16 
        if nd<16:
            nd=16
        self.stereo.setNumDisparities(nd)
        params["num_disp"][0]=nd
        
        block=params["block_size"][0]
        block-=(block%2-1) # block has a mimmun
        if block<1:
            block=1
        if self.method=="BM" and block<5:
            block=5
        self.stereo.setBlockSize(block) 
        params["block_size"][0]=block
        
        self.stereo.setUniquenessRatio(params["uniqueness"][0]) 
        self.stereo.setSpeckleRange(params["speckle_range"][0]) 
        self.stereo.setSpeckleWindowSize(params["speckle_window_size"][0]) 

              
        if self.method=="SGBM":
            P1,P2=self.get_p1_p2(params["window_size"][0])
            self.stereo.setP1(P1) 
            self.stereo.setP2(P2)

        self.params=params
        
        
    def get_p1_p2(self,window_size):
        # Recommended values for SGBM P1 & P2
        nc=1 # nc=3 for RGB
        return 8*nc*window_size**2,2*3*window_size**2 
    
