from socket import AF_INET, SOCK_DGRAM, socket
import threading
import numpy as np
import cv2
from multiprocessing import Pipe, Process
import time
from sys import platform
import math
import pickle as p

def contour_img(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    ret, threash, = cv2.threshold(gray, 127, 255, 0)
    cont, hie = cv2.findContours(threash, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(image, cont, -1, (0, 0, 0), 3 )
    return image

def udp_picture_transfer(pipe_recive, port):
    print("UDP thread started")
    video_stream_socket = socket(AF_INET, SOCK_DGRAM)
    ip = "10.0.0.1"
    max_pack_len = 60000
    while True:
        bilde = pipe_recive.recv()
        start = time.time()
        _, pack = cv2.imencode('.jpg',bilde)
        pack = pack.tobytes()
        pack_len = len(pack)
        counter = math.ceil(pack_len/max_pack_len)
        list = ['start', pack_len, counter]
        video_stream_socket.sendto(p.dumps(list), (ip, port))
        time.sleep(0.001)
        for x in range(5):
            if x*max_pack_len < pack_len:
                video_stream_socket.sendto(pack[(x*max_pack_len):(x+1)*max_pack_len],(ip, port))
            else:
                video_stream_socket.sendto(pack[(x*max_pack_len):-1],(ip, port))
                break
            #video_stream_socket.sendto(package[(x*61440):(x+1)*61440], ("127.0.0.1", 6888))
            #video_stream_socket.sendto(package[(x*61440):(x+1)*61440], ("127.0.0.1", 6888))
            time.sleep(0.0004)


#TODO click funksjon, Show image for debug/test 
def camera(camera_id, connection, picture_send_pipe):
    print("Camera Thread started")
    shared_list = [1, 0, 0, 0]
    picture = np.array
    conn_thread = threading.Thread(name="Camera_con", target=pipe_com, daemon=True, args=(connection, None, None, shared_list)).start()
    if platform == "linux" or platform == "linux2":
        feed = cv2.VideoCapture(camera_id,cv2.CAP_V4L2)
    else:
        feed = cv2.VideoCapture(camera_id, cv2.CAP_SHOW)
    feed.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
    feed.set(cv2.CAP_PROP_FRAME_WIDTH, 2560)
    feed.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    print(feed.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(feed.get(cv2.CAP_PROP_FRAME_WIDTH))
    feed.set(cv2.CAP_PROP_FPS, 30)
    feed.set(cv2.CAP_PROP_AUTOFOCUS, 1)
    run = True
    f_video_feed = True
    if not (feed.isOpened()):
        print("Could not open video device")
        run = False
    total_list = []
    while run:
        if not shared_list[0]:
            print("Message recived")
            print(shared_list[1])
            if shared_list[1] == "start_fedd":
                f_video_feed = True
            shared_list[0] = 1
        ref, frame = feed.read()
        crop_frame = frame[0:720, 0:1280]
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        if f_video_feed:
            picture_send_pipe.send(crop_frame)
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
        self.port_camback_feed = 6888
        self.port_camfront_feed = 6889


    #!TODO Tage?? Klare du å sjekka hardware id eller noge?
    def check_hw_id_cam(self):
        pass

    def toggle_front(self):
        if self.camera_status[0]:
            self.front_camera_prosess.kill()
            self.camera_status[0] = 0
        else:
            self.host_cam1, self.client_cam1 = Pipe()
            send_front_pic, recive_front_pic = Pipe()
            self.front_camera_prosess = Process(target=camera, daemon=True, args=(2, self.client_cam1, send_front_pic)).start()
            self.front_cam_com_thread = threading.Thread(name="COM_cam_1",target=pipe_com, daemon=True, args=(self.host_cam1, self.camera_com_callback, self.cam_front_name)).start()
            self.steam_video_prosess = Process(target=udp_picture_transfer, daemon=True, args=(recive_front_pic, self.port_camfront_feed)).start()
            self.camera_status[0] = 1

    def toggle_back(self):
        if self.camera_status[1]:
            self.back_camera_prosess.kill()
            self.camera_status[0] = 0
        else:
            self.host_cam2, self.client_cam2 = Pipe()
            send_back_pic, recive_back_pic = Pipe()
            self.back_camera_prosess = Process(target=camera, daemon=True, args=(0, self.client_cam2, send_back_pic)).start()
            self.front_cam_com_thread = threading.Thread(name="COM_cam_2",target=pipe_com, daemon=True, args=(self.host_cam2, self.camera_com_callback, self.cam_front_name)).start()
            self.steam_video_prosess = Process(target=udp_picture_transfer, daemon=True, args=(recive_back_pic, self.port_camback_feed)).start()
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
    for __ in range(9999999):
        time.sleep(1)
