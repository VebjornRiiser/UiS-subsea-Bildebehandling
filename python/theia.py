from ast import While, arg
from ctypes import sizeof
from json.tool import main
from re import U
from socket import AF_INET, SOCK_DGRAM, socket
from sqlite3 import connect
import threading
from unicodedata import name
import numpy as np
import cv2
from multiprocessing import Pipe, Process
import time
import math
from sys import platform

def contour_img(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    ret, threash, = cv2.threshold(gray, 127, 255, 0)
    cont, hie = cv2.findContours(threash, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(image, cont, -1, (0, 0, 0), 3 )
    return image

#TODO click funksjon, Show image for debug/test 
def camera(camera_id, connection):
    print("Camera Thread started")
    shared_list = [1, 0, 0, 0]
    picture = np.array
    conn_thread = threading.Thread(name="Camera_con", target=pipe_com, daemon=True, args=(connection, None, None, shared_list)).start()
    if platform == "linux" or platform == "linux2":
        feed = cv2.VideoCapture(camera_id)
    else:
        feed = cv2.VideoCapture(camera_id, cv2.CAP_SHOW)
    feed.set(3, 640)
    feed.set(4, 480)
    run = True
    f_video_feed = True

    if not (feed.isOpened()):
        print("Could not open video device")
        run = False
    video_stream_socket = socket(AF_INET, SOCK_DGRAM)
    while run:
        if not shared_list[0]:
            print("Message recived")
            print(shared_list[1])
            if shared_list[1] == "start_fedd":
                f_video_feed = True
            shared_list[0] = 1
        ref, frame = feed.read()
        #frame = contour_img(frame)
        cv2.imshow("feed", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        if f_video_feed:
            package = frame.flatten().tobytes()
            for x in range(15):
                video_stream_socket.sendto(package[(x*61440):(x+1)*61440], ("127.0.0.1", 6888))
    connection.send("Quit")
    feed.release()
    cv2.destroyAllWindows()

def pipe_com(connection, callback=None, name=None, list=None):
    if callback is not None:
        while True:
            msg = connection.recv()
            callback(msg, name)
    else:
        while list[0]:
            list[1] = print(connection.recv())
            list[0] = 0


#TODO cli_runtime
#Funksjon som håndterer en commandline interface for prossesser (slik at man kan styre ting når man tester)
# Denne skulle kanskje vært en toggle funksjon som man kan enable fra click når man kjører programmet


class Theia():
    def __init__(self) -> None:
        self.camera_status = [0, 0] #Index 0 = Camera front, Index 1 = Camera under/back
        self.camera_function = [0,0,0,0] # Inex 0 = Camera 1
        self.autonom = False # If true will send feedback on ROV postion related to red line etc.
        self.camera_front_id = 9 # Set to 9, so will fail if corret id is not set
        self_camera_back_id = 9 # Set to 9, so will fail if corret id is not set
        self.hardware_id_front = "asdopasud809123123"
        self.cam_front_name = "tage"
        self.cam_back_name = "mats"


    #!TODO Tage?? Klare du å sjekka hardware id eller noge?
    def check_hw_id_cam(self):
        pass

    def toggle_front(self):
        if self.camera_status[0]:
            self.front_camera_prosess.kill()
            self.camera_status[0] = 0
        else:
            self.host_cam1, self.client_cam1 = Pipe()
            self.front_camera_prosess = Process(target=camera, daemon=True, args=(2, self.client_cam1)).start()
            self.front_cam_com_thread = threading.Thread(name="COM_cam_1",target=pipe_com, daemon=True, args=(self.host_cam1, self.camera_com_callback, self.cam_front_name)).start()
            self.camera_status[0] = 1

    def toggle_back(self):
        if self.camera_status[1]:
            self.back_camera_prosess.kill()
            self.camera_status[0] = 0
        else:
            self.host_cam2, self.client_cam2 = Pipe()
            self.back_camera_prosess = Process(target=camera, daemon=True, args=(0, self.client_cam2)).start()
            self.front_cam_com_thread = threading.Thread(name="COM_cam_2",target=pipe_com, daemon=True, args=(self.host_cam2, self.camera_com_callback, self.cam_front_name)).start()
            self.camera_status[1] = 1

    def camera_com_callback(self, msg, name):
        if name == self.cam_front_name:
            print("Message revived from front camera: "+ msg)
            self.camera_status[0] = 0

        elif name == self.cam_back_name:
            print("Message revived back camera: "+ msg)
            self.camera_status[1] = 0

    def send_camera_func(self, camera_id, msg):
        if camera_id == 1: # MSG TO FRONT CAMERA
            self.host_cam1.send(msg)
        elif camera_id == 2: # MSG TO BACK CAMERA
            self.host_cam2.send(msg)



#INFO https://docs.opencv.org/4.x/d8/dfe/classcv_1_1VideoCapture.html
# Bruke grap og retrive når man bruker flere kameraer (Er vist den riktige måten å gjøre det på)



if __name__ == "__main__":
    print("Main=Theia")
    s = Theia()
    s.toggle_front()
    for __ in range(10):
        time.sleep(1)
