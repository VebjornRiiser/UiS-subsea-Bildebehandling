from ast import While
from email import message
from importlib import import_module
import threading, mjpeg_stream, cv2, time, math
from socket import AF_INET, SOCK_DGRAM, socket
import numpy as np
from multiprocessing import Pipe, Process
from subprocess import Popen, PIPE
import time
from sys import platform
import pickle as p
from yolo_detect import Yolo
import statistics
import matplotlib
# matplotlib.use('tkAgg') # This broke the code
from matplotlib import pyplot as plt
from common import *
from vision_pipline import picure_stich
#from distance import contour_img, calc_size, calc_distance

class Object(): # Used in functions to draw on image, find distance to objects etc, refers to objects in pictures
    def __init__(self, contour  ) -> None:
        self.rectanlge = cv2.minAreaRect(contour)
        self.angle = self.rectanlge[2]
        self.box = [np.int0(cv2.boxPoints(self.rectanlge))] # Added into a list due to easier use in draw contours
        self.position = (int(self.rectanlge[0][0]), int(self.rectanlge[0][1]))
        self.width = int(self.rectanlge[1][0])
        self.height = int(self.rectanlge[1][1])
        self.true_width = 0
        self.areal = self.width*self.height
        self.contour = contour
        self.dept = 0

    @property
    def get_box(self):
        return self._box

    @property
    def get_rectangle(self):
        return self._rectanlge

    @property
    def get_position(self):
        return self._position
    
    @property
    def get_width(self):
        return self._width

    @property
    def get_height(self):
        return self._height

    @property
    def get_areal(self):
        return self._areal

    @property
    def get_contour(self):
        return self._contour

    @property
    def get_dept(self):
        return self._dept

    def set_dept(self, newdept):
        self._dept = newdept

    @property
    def get_true_width(self):
        return self._true_width

    def set_true_width(self, newwidth):
        self._true_width = newwidth


def contour_img(image): # Finds shapes by color and size
    cvt_pic = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    color_lower = np.array([60,100,50])
    color_upper = np.array([160,255,255])
    mask = cv2.inRange(cvt_pic, color_lower, color_upper)
    cv2.erode(mask,np.ones((5,5),np.uint8), mask)
    ret, threash, = cv2.threshold(mask, 80, 255, 1)

  
    cont, hie = cv2.findContours(threash, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    ny_cont = []
    liste_paa_Sizes = list(map(cv2.contourArea , cont))
    for index, areal in enumerate(liste_paa_Sizes):
        if 5000 < areal < 500000:
            ny_cont.append(Object(cont[index]))
    if len(ny_cont) > 0:
        for object in ny_cont:
            cv2.drawContours(image, object.box , -1, (0, 0, 0), 2 )
    return ny_cont


def calc_size(num_pixels:int, centers, axis:int=0): # Calulates size of objects in picture
    """Calculates size with center points and number of pixelse size of object, axis=0 refers to horisontal measurment"""
    factor = -0.002344
    constant = 0.541
    dist = abs(centers[0][0]-centers[1][0])
    #print(f'Distance between pic: {dist}, Object size: {num_pixels}')
    return round((dist * factor + constant)*num_pixels, 1)


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
        self.middley = int(height/2) # Center of picture y cord
        self.width = width
        self.hud = True
        tru_width = int(width/2)
        self.length = int(width/18) # Long horisontal line for pitch
        self.length2 = int(width/22) # Short horisontal line for pitch
        self.length3 = int(width/36) # Cursor length
        self.length4 = int(self.length3/4) # Cursor spacing and triangle side length
        self.center = (width/4, height/2) # Center of picture
        self.squarestart = [int(self.center[0]-self.length-self.length4-100), int(self.center[1]-self.length)]
        self.squarestop = [int(self.center[0]-self.length-self.length4-60), int(self.center[1]+self.length)]
        self.cursor = Cursor(self.length3, self.length4, self.center)
        self.left = int(width/4-self.length3/2)
        self.right = int(width/4+self.length3/2)
        self.color = (0, 255, 0)
        self.sensor = {"gyro": (0, 0, 0)}
        if platform == "linux" or platform == "linux2":
            self.feed = cv2.VideoCapture(self.id, cv2.CAP_V4L2)
        else:
            self.feed = cv2.VideoCapture(self.id)
        self.set_picture_size(self.width, self.height)
        #self.feed.set(cv2.CAP_PROP_FPS, framerate)
        self.feed.set(cv2.CAP_PROP_AUTOFOCUS, 3)
        #self.feed.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)
        self.feed.set(cv2.CAP_PROP_EXPOSURE, 500)
        #self.feed.set(cv2.CAP_PROP_AUTO_WB, 1)
        print(self.feed.get(cv2.CAP_PROP_FPS))
        with open('cal_cam.npy', 'rb') as f:
            self.mtx1 = np.load(f)
            self.dist1 = np.load(f)
            self.mtx2 = np.load(f)
            self.dist2 = np.load(f)
            self.R = np.load(f)
            self.T = np.load(f)


    def set_picture_size(self, width:int=2560, height:int=960):
        self.feed.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
        self.feed.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.feed.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.height = int(self.feed.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.width = int(self.feed.get(cv2.CAP_PROP_FRAME_WIDTH))
        print(f'{self.width}:{self.height}')
        self.crop_width = int(self.width/2)

    def aq_image(self, double:bool=False, t_pic:bool=False):
        #ref, frame = self.feed.read()
        #frame = cv2.rotate(frame, cv2.ROTATE_180)
        #ref, frame = self.feed.read()
        ref = self.feed.grab()
        if ref:
            _, frame = self.feed.retrieve(0)
        else:
            if double:
                return False, False
            else:
                print(time.asctime())
                return False
        if frame is None:
            if double:
                return False, False
            else:
                print(time.asctime())
                return False
        frame = cv2.rotate(frame, cv2.ROTATE_180)
        crop = frame[:self.height, :self.crop_width]
        crop = cv2.undistort(crop, self.mtx1, self.dist1)
        crop2 = frame[:self.height,self.crop_width:]
        crop2 = cv2.undistort(crop2, self.mtx2, self.dist2)
        if t_pic:
            t = time.asctime()
            ln('Took picture')
            cv2.imwrite(f'/home/subsea/Bilete/rov/pic_left{t}.png',crop)
            cv2.imwrite(f'/home/subsea/Bilete/rov/pic_right{t}.png', crop2)
        if double:
            crop2 = frame[:self.height,self.crop_width:]
            return crop, crop2
        else:
            return crop

    ## Draws on image
    def draw_on_img(self, pic, frames):
        if isinstance(frames, list):
            if frames != []:
                for item in frames: # Draws objects on picture
                    cv2.rectangle(pic, item.rectangle[0], item.rectangle[1], item.colour, item.draw_line_width) # Draws rectablge on picture
                    pos = (item.rectangle[0][0], item.rectangle[0][1]+40) # For readability
                    cv2.putText(pic, item.name, pos, cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 3) # Red text
                    cv2.putText(pic, item.name, pos, cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 1) # White background
                    if item.dept != 0: # Draws dept esitmation if there is one
                        cv2.putText(pic, f'Distance:{int(item.dept)} cm',item.position, cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 3, cv2.LINE_AA)
                        cv2.putText(pic, f'Distance:{int(item.dept)} cm',item.position, cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2, cv2.LINE_AA)
        if self.hud:
            self.draw_hud(pic)
    
    def draw_hud(self, pic):
        for a in range(-20,21, 5):
            off = int(self.sensor['gyro'][2]*20+a*20 + self.middley)
            if 0 < off < self.height:
                if(a%2==0):
                    length = self.length
                else:
                    length = self.length2
                cv2.line(pic, (self.right, off), (self.right+length, off), self.color, 2) # 20 deg right
                cv2.putText(pic, f'{a}', (int(self.right+length+10), int(off+5)), cv2.FONT_HERSHEY_SIMPLEX, 1, self.color, 2) # 20 deg right text
                cv2.line(pic, (self.left-length, off), (self.left, off), self.color, 2) # 20 deg left
                #cv2.putText(pic, f'{a}', (self.left-length-45, off+5), cv2.FONT_HERSHEY_SIMPLEX, 1, self.color, 2) # 20 deg left text
        dept = self.sensor['gyro'][0]
        cv2.rectangle(pic, self.squarestart, self.squarestop, self.color, 2)
        cv2.putText(pic, f'Dept', (int(self.squarestart[0]-10) ,int(self.squarestart[1]-10)), cv2.FONT_HERSHEY_SIMPLEX, 1, self.color, 2)
        cv2.putText(pic, f'{dept}', (int(self.squarestart[0]-10), int(self.center[1])), cv2.FONT_HERSHEY_SIMPLEX, 1, self.color, 2)
        offset = dept - int(dept/10)
        dep_text = int(int(dept/10)*10)
        for a in range(0 , 100 , 10):
            cv2.line(pic, (int(self.squarestart[0]+4), int(self.squarestart[1]+a*3+offset)), (int(self.squarestop[0]-4), int(self.squarestart[1]+a*3+offset)), self.color, 2)
            if a != 50:
                cv2.putText(pic, f'{(dep_text-a+50)*-20}', (int(self.squarestart[0]), int(self.squarestart[1]+a*3+offset)), cv2.FONT_HERSHEY_SIMPLEX, 1, self.color, 2)
        points = np.array(self.cursor.get_points(self.sensor['gyro'][1]))
        cv2.polylines(pic, [points], False, (0,0,255), 2)

    def update_data(self, sens):
        self.sensor = sens


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


def find_same_objects(obj_list1:list, obj_list2:list, images): # This code will now brake Christoffer 1/4 -2022, calc distance is changed
    #plt.imshow(disp, 'gray')
    #plt.show()
    checked_object_list = []
    for obj1 in obj_list1:
        for obj2 in obj_list2:
            if obj1.position[1]-100 <= obj2.position[1] <= obj1.position[1]+100:
                #if obj1.width[1]-100 <= obj2.width[1] <= obj1.width[1]+100:
                obj1.dept = calc_distance([obj1.position, obj2.position])
                checked_object_list.append(obj1)
    return checked_object_list


## After objects are found this class can compare pictures and objects to determin if they could be the same object with the use of size and positions ##
## If objects match, will try to determin the diffrence in position theese objects have in the picture. ##
class Athena(): 
    def __init__(self) -> None:
        self.orb = cv2.ORB_create()
        self.bf = cv2.BFMatcher.create(cv2.NORM_HAMMING, crossCheck=True )
        self.first = True
        self.old_object_list = []
        
    # Diffrent methods to compare pixels in multiple pictures
    #stereo = cv2.StereoBM_create(numDisparities=16, blockSize=9)
    # 1
    #sift = cv2.SIFT_create()
    
    # 2
    #orb = cv2.ORB_create()
    #bf = cv2.BFMatcher()# OLD VERSION, THX OPENCV
    #bf = cv2.BFMatcher.create(cv2.NORM_HAMMING, crossCheck=True )

    # 3
    #cv2.FlannBasedMatcher(index_paralgorithm = 1, trees = 5, checks = 50) # index_paralgorithm = FLANN_INDEX_KDTREE = 1
    def check_last_size(self, new_object_list):
        if self.first:
            self.first = False
            self.old_object_list = new_object_list
            return new_object_list
        if len(new_object_list) == len(self.old_object_list):
            for a, obj in enumerate(new_object_list): # Checks each object if its within 20% of old size and position
                if self.old_object_list[a].width*0.8 < obj.width < self.old_object_list[a].width*1.2:
                    #if self.old_object_list[a].position[0]*0.8 < obj.position[0] < self.old_object_list[a].position[0]*1.2:
                    if obj.dept <= 0:
#                        ln(f"{obj.dept}, {self.old_object_list[a].dept}")
                        obj.dept = self.old_object_list[a].dept
                    elif self.old_object_list[a].dept <= 50:
                        pass
                    else:
 #                       ln(f"{obj.dept}, {self.old_object_list[a].dept}")
                        obj.dept = self.old_object_list[a].dept*0.8 + obj.dept*0.2
        elif len(new_object_list) == 0 and len(self.old_object_list) != 0:
            return self.old_object_list
        self.old_object_list = new_object_list
        return self.old_object_list


    def compare_pixles(self, object_list1, object_list2, pic):
        gray = [cv2.cvtColor(pic[0], cv2.COLOR_BGR2GRAY), cv2.cvtColor(pic[1], cv2.COLOR_BGR2GRAY)]
        new_object_list = []
        for obj1 in object_list1:
            for obj2 in object_list2:
                if obj1.position[1]-100 <= obj2.position[1] <= obj1.position[1]+100:
                    if obj1.width-50 <= obj2.width <= obj1.width+50:
                        points = [] # points to crop
                        points.append(int(obj1.rectangle[0][1]-obj1.height*0.1)) 
                        points.append(int(obj2.rectangle[0][1]-obj2.height*0.1)) 
                        points.append(int(obj1.rectangle[0][1]+obj1.height*1.1)) 
                        points.append(int(obj2.rectangle[0][1]+obj2.height*1.1)) 
                        points.append(int(obj1.rectangle[0][0]-obj1.width*0.1)) 
                        points.append(int(obj2.rectangle[0][0]-obj1.width*0.1)) 
                        points.append(int(obj1.rectangle[0][0]+obj1.width*1.1)) 
                        points.append(int(obj2.rectangle[0][0]+obj1.width*1.1)) 
                        for b, a in enumerate(points): # Checks that all points are within picture before crop
                            if a < 0:
                                points[b] = 0
                            if b <= 3:
                                if a > 720:
                                    points[b] = 720
                            else:
                                if a > 1280:
                                    points[b] = 1280
                        crop1 = gray[0][points[0]:points[2], points[4]:points[6]]
                        crop2 = gray[1][points[1]:points[3], points[5]:points[7]]
                        offset = obj1.rectangle[0][0]- obj2.rectangle[0][0]

                        # Testprints
                        #print(f'pos0:{int(obj1.rectangle[0][0])}')
                        #print(f'pos1:{int(obj1.rectangle[0][1])}')
                        #a = int(obj1.rectangle[0][0]+obj1.height*0.2)-int(obj2.rectangle[0][0]+obj1.height*0.2)
                        #b = obj1.rectangle[0][0]- obj2.rectangle[0][0]
                        #print(f'{(a==b)}')
                        #print(f'Offset:{offset}')
                        #print(f'Width1:{obj1.width}, height1:{obj1.height}')
                        #print(f'Width2:{obj2.width}, height2:{obj2.height}')
                        #cv2.imshow("TAGE1!!!!", crop1)
                        #cv2.imshow("TAGE2!!!!", crop2)
                        #if cv2.waitKey(1) & 0xFF == ord('q'):
                        #        break
                        
                        kp1, des1 = self.orb.detectAndCompute(crop1 ,None)
                        kp2, des2 = self.orb.detectAndCompute(crop2 ,None)
                        try:
                            mached_pixels = self.bf.match(des1, des2)
                            mached_pixels = sorted(mached_pixels, key = lambda x:x.distance)
                            print(len(mached_pixels))
                            new_list = []
                            for a in mached_pixels:
                                if a.distance < 100:
                                    new_list.append(a)
                        except Exception as i:
                            print(i)
                            return
                        mached_pixels = new_list
                        #imgDummy = np.zeros((1,1))
                        #img = cv2.drawMatches(crop1,kp1,crop2,kp2,mached_pixels[:10], imgDummy, flags=2)
                        #cv2.imshow("TAGE1!!!!", img)
                        dif_list = []
                        if len(mached_pixels) > 2:
                            for a in mached_pixels:
                                if abs(kp1[a.queryIdx].pt[1] - kp2[a.trainIdx].pt[1]) < 10:
                                    crop1 = cv2.circle(crop1, (int(kp1[a.queryIdx].pt[0]), int(kp1[a.queryIdx].pt[1])), 4, (255,0,0), -1)
                                    crop2 = cv2.circle(crop2, (int(kp2[a.trainIdx].pt[0]), int(kp2[a.trainIdx].pt[1])) , 4, (255,0,0), -1)
                                    dif_list.append(abs(kp1[a.queryIdx].pt[0] - kp2[a.trainIdx].pt[0]+offset))
                            if len(dif_list) > 2:   
                                med = statistics.median(dif_list)
                                if 158 < med < 218:
                                    obj1.dept = calc_distance(med)
                                    ln(f"{obj1.dept}")
                                
                                # Print for calibration
                                #print(f'Disparity: {statistics.median(dif_list)}')
                                
                                #cv2.imshow("TAGE1!!!!", crop1)
                                #cv2.imshow("TAGE2!!!!", crop2)
                                #if cv2.waitKey(1) & 0xFF == ord('q'):
                                #    break
                                #pass
                                #print(f'Mean:{statistics.mean(dif_list)}')
                                #print(f'Median:{statistics.median(dif_list)}')
                        #plt.imshow(img),plt.show()
                        #cv2.imshow("TAGE2!!!!", crop2)
                        #if cv2.waitKey(1) & 0xFF == ord('q'):
                        #    break
            new_object_list.append(obj1)
        if len(new_object_list) > 1:
            new_object_list = check_overlap(new_object_list) # Checks for object overlapping
        new_object_list = self.check_last_size(new_object_list) # Filters distances vales, and sets old if new is not found
        return new_object_list

## Recives images and processes them according to mode returns objects with information to draw, len to objects and positions related to them ##
def image_aqusition_thread(connection, boli):
    time_list = []
    mode = 1 # 1: Find rubberfish, 2: mosaikk 3:TBA 
    #TODO Her skal autonom kjøring legges inn
    old_list = []
    first = True
    width = 1280

    st_list = [] # List of images to stitch
    ath = Athena()
    new_pic = False
    stitch = False
    while boli:
        mess = connection.recv()
        if isinstance(mess, list):
            if first:
                first = False
                s = mess[0].shape
                yal = Yolo((s[1], s[0]))
        if isinstance(mess, str):
            if mess.lower() == 'stop': # Stoppes thread
                break
            elif mess.lower() == 'fish': # Sets mode
                mode = 1
            elif mess.lower() == 'automerd':
                mode = 2
            elif mess.lower() == 'mosaikk': # Sets mode
                ln('Mode in IA set to  3')
                mode = 3
            elif mess.lower() == 'tpic': # Take new picture and append to image list
                new_pic = True
            elif mess.lower() == 'stitch': # Use current image list and stitch images
                stitch = True
        else:
            if mode == 1:
                start = time.time()
                mached_list = []
                if len(mess) == 2:
                    res1 = yal.yolo_image(mess[0]) # Result from left cam
                    res2 = yal.yolo_image(mess[1]) # Result from right cam
                    if len(res1) > 0 and len(res2) > 0:
                        #mached_list = find_same_objects(res1, res2, mess) # Old funtion
                        mached_list = ath.compare_pixles(res1, res2, mess)
                #time_list.append(time.time()-start)
                connection.send(mached_list)
            elif mode == 2:
                #!! TODO Place function  here
                pass
            elif mode == 3:
                if new_pic:
                    new_pic = False
                    st_list.append(mess[0])
                    ln('New pic appended')
                elif stitch:
                    stitch = False
                    if len(st_list) > 1:
                        pic = picure_stich(st_list)
                        st_list = []
                        if pic != []:
                            ln('Successfully stiched images')
                            cv2.imwrite(f'/home/subsea/Bilete/mosaikk/Stitch{time.asctime()}.png',pic)
                        else:
                            ln('Failed to stich image')
                    else:
                        ln('List too short cant stitch image')
        if len(time_list) > 20:
            #print(statistics.mean(time_list))
            time_list = []
        


## Got access to one camera, can aquire images from camera, communicates with main process and can send picutres to image prossesing and stream ##
def camera_thread(camera_id, connection, picture_send_pipe, picture_IA_pipe, local = False):  
    print(f'Camera:{camera_id} started')
    cam = Camera(camera_id)
    shared_list = [1, 0, 0, 0]
    threading.Thread(name="Camera_con", target=pipe_com, daemon=True, args=(connection, None, None, shared_list)).start()
    fourcc = cv2.VideoWriter_fourcc(*'MPEG')
    run = True
    video_feed = not local
    video_capture = False
    take_pic = False
    mode = shared_list[2] # Camera modes: 0: Default no image processing, 1: Find shapes and calculate distance to shapes, 2: ??, 3 ?? 
    if not (cam.feed.isOpened()):
        print('Could not open video device')
        run = False
    frame_count = 1 # Used to only skip some frames for image AQ
    draw_frames = []
    if not video_feed:
        cv2.namedWindow('FishCam', cv2.WINDOW_NORMAL)
    while run:
        if shared_list[1] == 1:
            shared_list[1] = 0
            if shared_list[2] == "video":
                video_capture ^= True
                if video_capture:
                    print("Started creating video file")
                    video_write = cv2.VideoWriter(f'vid_{time.asctime()}.mp4', fourcc, 30.0, (cam.crop_width, cam.height))
                else:
                    print("Video finished")
                    video_write.release()
            elif shared_list[2] == "tpic":
                take_pic = True
                picture_IA_pipe.send(shared_list[2])
            elif shared_list[2] == 'stitch':
                picture_IA_pipe.send(shared_list[2])                     
            elif shared_list[2] == 'stop':
                print('Camera thread stopped')
                picture_send_pipe.send('stop')
                connection.send('stop')
                cam.feed.release()
                cv2.destroyAllWindows()
                break
            elif shared_list[2] == 'sensor':
                cam.update_data(shared_list[3])
                shared_list[3] = 0
            elif shared_list[2] == 'hud':
                cam.hud != cam.hud
            else:
                if isinstance(shared_list[2], int):
                    mode = shared_list[2]
                    print(f'Mode set to {mode}')
                    if shared_list[2] == 3:
                        picture_IA_pipe.send('mosaikk')
                    mode = int(mode)
                else:
                    ln(f'Cameramode: {shared_list[2]}, is not supported')
                    shared_list[1] = 0
        if mode == 0:
            pic = cam.aq_image(False, take_pic)
            take_pic = False
            if pic is False:
                cam.feed.release()
                cv2.destroyAllWindows()
                cam = Camera(camera_id)
        elif mode == 1:
            pic, pic2 = cam.aq_image(True, take_pic)
            take_pic = False
            if pic is False:
                cam.feed.release()
                cv2.destroyAllWindows()
                cam = Camera(camera_id)
            frame_count += 1
            if frame_count > 9:
                frame_count = 0
                if picture_IA_pipe.poll():
                    draw_frames = picture_IA_pipe.recv()
                picture_IA_pipe.send([pic, pic2])
        elif mode == 3:
            pic, pic2 = cam.aq_image(True, take_pic)
            take_pic = False
            if pic is False:
                cam.feed.release()
                cv2.destroyAllWindows()
                cam = Camera(camera_id)
            picture_IA_pipe.send([pic, pic2])
        if mode == 5:
            time.sleep(3)
        elif video_feed:
            cam.draw_on_img(pic, draw_frames)
            picture_send_pipe.send(pic)
        else:
            cv2.imshow('FishCam',pic)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        if video_capture:
            video_write.write(pic)
    if video_capture:
        video_write.release()
    print("Video thread stopped")
    cam.feed.release()
    cv2.destroyAllWindows()
        

#TODO click funksjon, Show image for debug/test 
def camera(camera_id, connection, picture_send_pipe):
    print("Camera Thread started")
    shared_list = [1, 0, 1, 0]
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
    f_video_feed = False
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
            if isinstance(list[2], dict):
                list[3] = list[2] # Dictionary stored in index 3, can be dept, orientation etc
                list[2] = 'sensor' # Codeword for sensor data
            list[1] = 1

## Checks if object positions overlap ##
# Returns list without overlap #  
# Function needs to be tested #
def check_overlap(obj_list): 
    del_list = []
    for a, b in enumerate(obj_list):
        if a != len(obj_list)-1:
            for obj in obj_list[a+1:]:
                if obj.rectangle[0][0] < b.position[0] < obj.rectangle[1][0]:
                    if obj.rectangle[0][1] < b.position[1] < obj.rectangle[1][1]:
                        del_list.append(b)
                        break
    for a in del_list:
        obj_list.remove(a)
    return obj_list

#TODO cli_runtime
# Funksjon som håndterer en commandline interface for prossesser (slik at man kan styre ting når man tester)
# Denne skulle kanskje vært en toggle funksjon som man kan enable fra click når man kjører programmet


class Theia():
    def __init__(self) -> None:
        self.camera_status = {'front':[0,0], 'back':[0,0]} # Camera status, index 0 : Availability, index 1: Status
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
        self.cam_front_id = self.find_cam("3-2.7") # Checks if a camera is connected on this port
        self.cam_back_id = self.find_cam(".5")
        #self.cam_front_id = self.find_cam("004")
        #self.cam_back_id = self.find_cam("007")
        if not self.cam_front_id:
            print(f'Did no find front camera')
            self.camera_status['front'][1] = 0
        else:
            print(f'Found front camera')
            self.camera_status['front'][1] = 1
        if not self.cam_back_id:
            print(f'Did no find back camera')
            self.camera_status['back'][1] = 0
        else:
            print(f'Found back camera')
            self.camera_status['back'][1] = 1

    def find_cam(self, cam):
        cmd = ["/usr/bin/v4l2-ctl", "--list-devices"]
        out, err = Popen(cmd, stdout=PIPE, stderr=PIPE).communicate()
        out, err = out.strip(), err.strip()
        for l in [i.split("\n\t") for i in out.decode("utf-8").split("\n\n")]:
            if cam in l[0]:
                return l[1]
        return False

    def toggle_front(self, local: bool=False):
        #print(f"{self.camera_status['front'] = }")
        if self.camera_status['front'][0] == 1:
            self.host_cam_front.send('stop')
            self.camera_status['front'][0] = 0
            return "Camera front stopped"
        else:
            if self.camera_status['front'][1]:
                self.host_cam_front, self.client_cam1 = Pipe()
                self.send_front_pic, recive_front_pic = Pipe()
                send_IA_front, recive_IA = Pipe()
                self.front_camera_prosess = Process(target=camera_thread, daemon=True, args=(self.cam_front_id, self.client_cam1, self.send_front_pic, send_IA_front, local))
                self.front_camera_prosess.start()
                self.front_cam_com_thread = threading.Thread(name="COM_cam_1",target=pipe_com, daemon=True, args=(self.host_cam_front, self.camera_com_callback, self.cam_front_name)).start()
                self.steam_video_prosess = Process(target=mjpeg_stream.run_mjpeg_stream, daemon=True, args=(recive_front_pic, self.port_camfront_feed)).start()
                self.camera_status['front'][0] = 1
                self.image_AQ_process = Process(target=image_aqusition_thread, daemon=True, args=(recive_IA, True))
                self.image_AQ_process.start()
                return "Camera front started"
            else:
                return "Camera front is not connected"

    def toggle_back(self, local: bool=False):
        print(self.camera_status['back'])
        if self.camera_status['back'][0] == 1:
            self.host_back.send('stop')
            self.camera_status['back'][0] = 0
            return "Camera back stopped"
        else:
            if self.camera_status['back'][1]:
                self.host_back, self.client_cam2 = Pipe()
                send_back_pic, recive_back_pic = Pipe()
                send_IA2, recive_IA2 = Pipe()
                self.back_camera_prosess = Process(target=camera_thread, daemon=True, args=(self.cam_back_id, self.client_cam2, send_back_pic, send_IA2, local)).start()
                self.front_cam_com_thread = threading.Thread(name="COM_cam_2",target=pipe_com, daemon=True, args=(self.host_back, self.camera_com_callback, self.cam_front_name)).start()
                self.steam_video_prosess = Process(target=mjpeg_stream.run_mjpeg_stream, daemon=True, args=(recive_back_pic, self.port_camback_feed)).start()
                self.camera_status['back'][0] = 1
                self.image_AQ_process2 = Process(target=image_aqusition_thread, daemon=True, args=(recive_IA2, True))
                self.image_AQ_process2.start()
                return "Camera back started"
            else:
                return "Camera back is not connected"

    def camera_com_callback(self, msg, name):
        if name == self.cam_front_name:
            #print("Message revived from front camera: "+ msg)
            self.camera_status[0] = 0

        elif name == self.cam_back_name:
            #print("Message revived back camera: "+ msg)
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
    #s.camera_status['front'][1] = 1
    #s.cam_front_id = 1
    
    s.toggle_front(local = True)
    #s.toggle_back()
    print(time.asctime())
    
    #s.toggle_back()
    for __ in range(9999999):
        time.sleep(5)
        #s.host_cam_front.send(0)
        #time.sleep(20)
        #s.host_cam_front.send(1)


                    # Noen ubrukte bildebehandlingsmetoder

                    #gray = [cv2.cvtColor(mess[0], cv2.COLOR_BGR2GRAY), cv2.cvtColor(mess[1], cv2.COLOR_BGR2GRAY)]
                    #points = sift.detect(gray[1], None)
                    #img=cv2.drawKeypoints(gray[1], points ,mess[0])
                    
                    
                    #new_list = []
                    #kp1, des1 = orb.detectAndCompute(gray[0] ,None)
                    #kp2, des2 = orb.detectAndCompute(gray[1] ,None)
                    #mached_pixels = bf.match(des1, des2)

                    #print(len(mached_pixels))
                    #for a in kp1:
                    #    print(a.pt)
                    
                    ### Some type of id from a list
                    #for a in mached_pixels:
                    #    print(kp1[a.trainIdx].pt)


                    #disp = stereo.compute(gray[0], gray[1])
                    #plt.imshow(disp, 'gray')
                    
                    # IMSHOWS FOR TEST
                    #plt.show()
                    #cv2.imshow('text', img)
                    #if cv2.waitKey(1) & 0xFF == ord('q'):
                    #    break
