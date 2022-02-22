from ast import While
from email import message
import threading, mjpeg_stream, cv2, time, math
from socket import AF_INET, SOCK_DGRAM, socket
import numpy as np
from multiprocessing import Pipe, Process
from subprocess import Popen, PIPE
import time
from sys import platform
import pickle as p
from distance import contour_img, calc_size, calc_distance


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
        for x in range(counter):
            if x*max_pack_len < pack_len:
                video_stream_socket.sendto(pack[(x*max_pack_len):(x+1)*max_pack_len],(ip, port))
            else:
                video_stream_socket.sendto(pack[(x*max_pack_len):-1],(ip, port))
                break
            time.sleep(0.001)


def white_balance(img):
    result = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    avg_a = np.average(result[:, :, 1])
    avg_b = np.average(result[:, :, 2])
    result[:, :, 1] = result[:, :, 1] - ((avg_a - 128) * (result[:, :, 0] / 255.0) * 1.1)
    result[:, :, 2] = result[:, :, 2] - ((avg_b - 128) * (result[:, :, 0] / 255.0) * 1.1)
    result = cv2.cvtColor(result, cv2.COLOR_LAB2BGR)
    return result


class Camera():
    def __init__(self, id:int, width:int=2560, height:int=720, framerate:int=30 ) -> None:
        self.id = id
        self.height = height
        self.width = width
        if platform == "linux" or platform == "linux2":
            self.feed = cv2.VideoCapture(self.id, cv2.CAP_V4L2)
        else:
            self.feed = cv2.VideoCapture(self.id, cv2.CAP_SHOW)
        self.set_picture_size(self.width, self.height)
        #self.feed.set(cv2.CAP_PROP_FPS, framerate)
        #self.feed.set(cv2.CAP_PROP_AUTOFOCUS, 1)
        #self.feed.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)
        #self.feed.set(cv2.CAP_PROP_EXPOSURE, 600)
        #self.feed.set(cv2.CAP_PROP_AUTO_WB, 1)
        print(self.feed.get(cv2.CAP_PROP_FPS))


    def set_picture_size(self, width:int=2560, height:int=960):
        self.feed.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
        self.feed.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.feed.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.height = int(self.feed.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.width = int(self.feed.get(cv2.CAP_PROP_FRAME_WIDTH))
        print(f'{self.width}:{self.height}')
        self.crop_width = int(self.width/2)

    def aq_image(self, double:bool=False):
        ref, frame = self.feed.read()
        #frame = cv2.rotate(frame, cv2.ROTATE_180)
        print(type(frame))
        crop = frame[:self.height, :self.crop_width]
        if crop is None:
            return False
        if double:
            crop2 = frame[:self.height,self.crop_width:]
            crop2 = white_balance(crop2)
            crop = white_balance(crop)
            return crop, crop2
        else:
            #crop = white_balance(crop)
            return crop


def find_calc_shapes(pic1, pic2):
    mached_list = []
    pic1 = white_balance(pic1)
    pic2 = white_balance(pic2)
    objects = contour_img(pic1)
    objects2 = contour_img(pic2)
    if len(objects) > 0 and len(objects2) > 0:
        for a in objects:
            for b in objects2:
                if (cv2.matchShapes(a.contour, b.contour, cv2.CONTOURS_MATCH_I1, 0.0)) < 0.3:
                    distance = calc_distance([a.position, b.position], 60, 6)
                    a.dept = distance
                    if distance > 10:
                        #cv2.putText(pic1, f'Distance:{distance} cm',a.position, cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 3, cv2.LINE_AA)
                        #cv2.putText(pic1, f'Distance:{distance} cm',a.position, cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2, cv2.LINE_AA)
                        width  = calc_size (a.width,(a.position,b.position) ,  0)
                        a.true_width = width
                        mached_list.append(a)
                        #cv2.putText(pic1, f'Width:{width} cm',(a.position[0], a.position[1]+50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 3, cv2.LINE_AA)
                        #cv2.putText(pic1, f'Width:{width} cm',(a.position[0], a.position[1]+50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2, cv2.LINE_AA)
    return mached_list


def image_aqusition_thread(connection, boli):
    mode = 1 # 1: Find fish, 2: mosaikk 3:TBA
    while boli:
        mess = connection.recv()
        if isinstance(mess, str):
            if mess.lower() == 'stop':
                break
            elif mess.lower() == 'fish':
                mode = 1
            elif mess.lower() == 'mosaikk':
                mode = 2
        else:
            if mode == 1:
                if len(mess) == 2:
                    mached_list = find_calc_shapes(mess[0], mess[1])
                    connection.send(mached_list)
            elif mode == 2:
                pass
        

def draw_on_img(pic, frames):
    for a in frames:
        cv2.putText(pic, f'Distance:{a.dept} cm',a.position, cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 3, cv2.LINE_AA)
        cv2.putText(pic, f'Distance:{a.dept} cm',a.position, cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2, cv2.LINE_AA)
        cv2.putText(pic, f'Width:{a.true_width} cm',(a.position[0], a.position[1]+50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 3, cv2.LINE_AA)
        cv2.putText(pic, f'Width:{a.true_width} cm',(a.position[0], a.position[1]+50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2, cv2.LINE_AA)
        cv2.drawContours(pic, a.box , -1, (0, 0, 0), 2 )

def camera_thread(camera_id, connection, picture_send_pipe, picture_IA_pipe):
    print(f'Camera:{camera_id} started')
    cam = Camera(camera_id)
    print("got passed class")
    shared_list = [1, 0, 0, 0]
    threading.Thread(name="Camera_con", target=pipe_com, daemon=True, args=(connection, None, None, shared_list)).start()
    run = True
    video_feed = True
    mode = shared_list[2] # Camera modes: 0: Default no image processing, 1: Find shapes and calculate distance to shapes, 2: ??, 3 ?? 
    print("Trying to enter loop")
    if not (cam.feed.isOpened()):
        print('Could not open video device')
        run = False
    frame_count = 1 # Used to only skip some frames for image AQ
    draw_frames = []
    while run:
        if shared_list[1] == 1:
            mode = shared_list[2]
            if isinstance(mode, str):
                if mode.lower() == 'stop':
                    picture_send_pipe('stop')
                    connection.send('stop')
                    run = False
        if mode == 0:
            pic = cam.aq_image()
            if pic is False:
                continue
        elif mode == 1:
            pic, pic2 = cam.aq_image(True)
            #pic = find_calc_shapes(pic, pic2)
            frame_count += 1
            if frame_count > 2:
                frame_count = 0
                if picture_IA_pipe.poll():
                    draw_frames = picture_IA_pipe.recv()
                picture_IA_pipe.send([pic, pic2])
            if draw_frames != []:
                draw_on_img(pic, draw_frames)
        elif mode == 5:
            time.sleep(2)
        if video_feed:
            picture_send_pipe.send(pic)
        else:
            cv2.imshow("Named Frame",pic)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    print("Video thread stopped")
    cam.feed.release()
    cv2.destroyAllWindows()
        

#TODO click funksjon, Show image for debug/test 
def camera(camera_id, connection, picture_send_pipe):
    print("Camera Thread started")
    shared_list = [1, 0, 0, 0]
    picture = np.array
    conn_thread = threading.Thread(name="Camera_con", target=pipe_com, daemon=True, args=(connection, None, None, shared_list)).start()
    if platform == "linux" or platform == "linux2":
        feed = cv2.VideoCapture(camera_id, cv2.CAP_V4L2)
    else:
        feed = cv2.VideoCapture(camera_id, cv2.CAP_SHOW)
    feed.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
    frame_width = 2560
    frame_height = 720
    feed.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
    feed.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)
    frame_height = int(feed.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_width = int(feed.get(cv2.CAP_PROP_FRAME_WIDTH))
    crop_width = int(frame_width/2)
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
        crop_frame = frame[:frame_height, :crop_width]
        #crop_frame = contour_img(crop_frame)
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
            if isinstance(msg, str):
                if msg.lower() == 'stop':
                    break
            callback(msg, name)
    else:
        while list[0]:
            list[2] = connection.recv()
            list[1] = 1
            #print(f"{list[1] = }")


#TODO cli_runtime
#Funksjon som håndterer en commandline interface for prossesser (slik at man kan styre ting når man tester)
# Denne skulle kanskje vært en toggle funksjon som man kan enable fra click når man kjører programmet


class Theia():
    def __init__(self) -> None:
        # Index 0 = id, index 1 = is running
        self.camera_status = {'front':[0,0], 'back':[0,0]}
        #self.camera_status = [0, 0] #Index 0 = Camera front, Index 1 = Camera under/back
        self.camera_function = {'front': False, 'back':False} # Bool = Pircutre prossesing status
        self.autonom = False # If true will send feedback on ROV postion related to red line etc.
        self.port_camback_feed = 6888
        self.port_camfront_feed = 6889
        self.cam_front_name = 'mats'
        self.cam_back_name =  'tage'
        self.set_front_zero = [200, {"tilt": 0}]
        self.set_back_zero = [201, {"tilt": 0}]
        self.check_hw_id_cam()

    def check_hw_id_cam(self):
        self.cam_front_id = self.find_cam(".5") # Finner kamera på usb
        self.cam_back_id = self.find_cam("4-2")
        if not self.cam_front_id:
            self.camera_status['front'][1] = 0
        else:
            self.camera_status['front'][1] = 1
        if not self.cam_back_id:
            self.camera_status['back'][1] = 0
        else:
            self.camera_status['back'][1] = 1

    def find_cam(self, cam):
        cmd = ["/usr/bin/v4l2-ctl", "--list-devices"]
        out, err = Popen(cmd, stdout=PIPE, stderr=PIPE).communicate()
        out, err = out.strip(), err.strip()
        for l in [i.split("\n\t") for i in out.decode("utf-8").split("\n\n")]:
            if cam in l[0]:
                return l[1]
        return False

    def toggle_front(self, cam_id: int=0):
        print(f"{self.camera_status['front'] = }")
        if self.camera_status['front'][0] == 1:
            self.host_cam_front.send('stop')
            self.camera_status['front'][0] = 0
        else:
            if self.camera_status['front'][1]:
                self.host_cam_front, self.client_cam1 = Pipe()
                send_front_pic, recive_front_pic = Pipe()
                send_IA, recive_IA = Pipe()
                self.front_camera_prosess = Process(target=camera_thread, daemon=True, args=(self.cam_front_id, self.client_cam1, send_front_pic, send_IA))
                self.front_camera_prosess.start()
                self.front_cam_com_thread = threading.Thread(name="COM_cam_1",target=pipe_com, daemon=True, args=(self.host_cam_front, self.camera_com_callback, self.cam_front_name)).start()
                self.steam_video_prosess = Process(target=mjpeg_stream.run_mjpeg_stream, daemon=True, args=(recive_front_pic, self.port_camfront_feed)).start()
                self.camera_status['front'][0] = 1
                self.image_AQ_process = Process(target=image_aqusition_thread, daemon=True, args=(recive_IA, True))
                self.image_AQ_process.start()
                return True
            else:
                return False

    def toggle_back(self, cam_id: int=2):
        print(self.camera_status['back'])
        if self.camera_status['back'][0] == 1:
            self.host_back.send('stop')
            self.camera_status['back'][0] = 0
        else:
            if self.camera_status['back'][1]:
                self.host_back, self.client_cam2 = Pipe()
                send_back_pic, recive_back_pic = Pipe()
                self.back_camera_prosess = Process(target=camera_thread, daemon=True, args=(self.cam_back_id, self.client_cam2, send_back_pic)).start()
                self.front_cam_com_thread = threading.Thread(name="COM_cam_2",target=pipe_com, daemon=True, args=(self.host_back, self.camera_com_callback, self.cam_front_name)).start()
                self.steam_video_prosess = Process(target=mjpeg_stream.run_mjpeg_stream, daemon=True, args=(recive_back_pic, self.port_camback_feed)).start()
                self.camera_status['back'][0] = 1
                return True
            else:
                return False

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
    print("test")
    #s.camera_status['front'][1] = 1
    #s.cam_front_id = 0
    
    s.toggle_front()
    
    #s.toggle_back()
    for __ in range(9999999):
        time.sleep(5)
        #s.host_cam_front.send(0)
        #time.sleep(20)
        #s.host_cam_front.send(1)
