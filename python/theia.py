from ast import While
from ctypes import sizeof
from json.tool import main
from multiprocessing import shared_memory
from re import U
from unicodedata import name
import numpy as np
import cv2
import multiprocessing
import time
import math
import zmq



#TODO click funksjon, Show image for debug/test 
def camera_loop(feed, flag = [1], show_img= True):
    while flag[0]:
        ret, frame = feed.read()
        if show_img:
            cv2.imshow()
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            else:
                # bilde = cv2.imencode('.jpg',frame)
                # bilde.tostring()
                video_source.send(frame)
                #TODO ADD CAMERA FEED!
                pass
        feed.release()
        cv2.destroyAllWindows()


def camera(camera_id, callback):
    picture = np.array
    feed = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)
    feed.set(3, 640)
    feed.set(4, 480)
    if not (feed.isOpened()):
        print("Could not open video device")
    while True:
        ref, frame = feed.read()
        cv2.imshow("feed", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    feed.release()
    cv2.destroyAllWindows()




#TODO cli_runtime
#Funksjon som håndterer en commandline interface for prossesser (slik at man kan styre ting når man tester)
# Denne skulle kanskje vært en toggle funksjon som man kan enable fra click når man kjører programmet


class Theia():
    def __init__(self) -> None:
        context = zmq.Context()
        self.intern_com = context.socket(zmq.PAIR)
        self.intern_com.connect("inproc//interncom")
        self.intern_com.send("test")
        self.camera_status = [0, 0] #Index 0 = Camera front, Index 1 = Camera under/back
        self.camera_function = [0,0,0,0] # Inex 0 = Camera 1
        self.autonom = False # If true will send feedback on ROV postion related to red line etc.
        self.camera_front_id = 9 # Set to 9, so will fail if corret id is not set
        self_camera_back_id = 9 # Set to 9, so will fail if corret id is not set
        self.hardware_id_front = "asdopasud809123123"

    #!TODO Tage?? Klare du å sjekka hardware id eller noge?
    def check_hw_id_cam(self):
        pass

    def toggle_front(self):
        if self.front_camera_prosess.is_alive():
            self.front_camera_prosess.kill()
            self.camera_status[0] = 0
        else:
            self.front_camera_prosess = multiprocessing.Process(target=camera, args=(0,))
            self.camera_status[0] = 1

    def toggle_back(self):
        if self.back_camera_prosess.is_alive():
            self.back_camera_prosess.kill()
            self.camera_status[0] = 0
        else:
            self.back_camera_prosess = multiprocessing.Process(target=camera, args=(0,))
            self.camera_status[0] = 1

    def intern_com_init(self):
        pass

    def intern_com_callback(self):
        pass
 
 
#INFO https://docs.opencv.org/4.x/d8/dfe/classcv_1_1VideoCapture.html
# Bruke grap og retrive når man bruker flere kameraer (Er vist den riktige måten å gjøre det på)



if __name__ == "__main__":
    print("funka")
    context = zmq.Context()
    video_source = context.socket(zmq.PAIR)
    camera_prossess = multiprocessing.Process(target=camera, args=(0,))
    camera_prossess2 = multiprocessing.Process(target=camera, args=(1,))
    #camera_prossess.start()
    #camera_prossess2.start()

