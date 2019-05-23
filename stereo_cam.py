# Multithreading: lectura de la camara en un th aparte
from threading import Thread, Lock
import cv2 as cv

class StereoCam:
    """Clase para leer camara stereo de forma continua en un thread independiente"""
    def __init__(self):
        self.cam=[cv.VideoCapture(1),cv.VideoCapture(0)] #
        
        self.im=[[],[]]
        self.started = False
        self.read_lock = Lock()
        
    def start(self):
        if self.started:
            return None
        self.started=True
        self.thread=Thread(target=self.get,args=())
        self.thread.start()
        return self
    def get(self):

        while self.started:
            im=[[],[]]
            for s in range(2):
                self.cam[s].grab()
            for s in range(2):
                _,im[s]=self.cam[s].retrieve()
            with self.read_lock:
                self.im=im
        
    def read(self):
        with self.read_lock:
            return list(self.im)

    def stop(self):
        self.started = False
        self.thread.join()

    def __exit__(self, exec_type, exc_value, traceback):
        self.cam[0].release()
        self.cam[1].release()
