from operator import pos
import cv2
from sys import platform
import numpy as np
import time

# TESTSCRIPT FOR AVSTANDSMÅLING + Funksjoner for beregning av avstand og størrlser på objekter

class Object():
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



def white_balance(img):
    result = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    avg_a = np.average(result[:, :, 1])
    avg_b = np.average(result[:, :, 2])
    result[:, :, 1] = result[:, :, 1] - ((avg_a - 128) * (result[:, :, 0] / 255.0) * 1.1)
    result[:, :, 2] = result[:, :, 2] - ((avg_b - 128) * (result[:, :, 0] / 255.0) * 1.1)
    result = cv2.cvtColor(result, cv2.COLOR_LAB2BGR)
    return result


def camera(camera_id):
    print("Camera Thread started")
    shared_list = [1, 0, 0, 0]
    picture = np.array
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
    print(crop_width)
    print(frame_width)
    print(frame_height)
    run = True
    feed.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
    feed.set(cv2.CAP_PROP_EXPOSURE, 600)
    if not (feed.isOpened()):
        print("Could not open video device")
        run = False
    total_list = []
    while run:
        ref, frame = feed.read()
        crop_frame = frame[:frame_height, :crop_width]
        crop_frame2 = frame[:frame_height,crop_width:]
        crop_frame = white_balance(crop_frame)
        crop_frame2 = white_balance(crop_frame2)
        crop_frame, cord, s1 = contour_img(crop_frame)
        crop_frame2, cord2, s2 = contour_img(crop_frame2)
        if len(cord) == 2 and len(cord2)==2:
            distance = calc_distance([cord, cord2], 60 , 6)
            if distance > 10:
                cv2.putText(crop_frame, f'Distance:{distance} cm',cord, cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 3, cv2.LINE_AA)
                cv2.putText(crop_frame, f'Distance:{distance} cm',cord, cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2, cv2.LINE_AA)
                width  = calc_size (s1[0],(cord,cord2) ,  0)
                cv2.putText(crop_frame, f'Width:{width} cm',(cord[0], cord[1]+100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2, cv2.LINE_AA)
        cv2.imshow("Named Frame",crop_frame)
        cv2.imshow("named Frame2", crop_frame2)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    feed.release()
    cv2.destroyAllWindows()


def contour_img(image):
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
        if areal > 5000 and areal < 500000:
            ny_cont.append(Object(cont[index]))
    if len(ny_cont) > 0:
        for object in ny_cont:
            cv2.drawContours(image, object.box , -1, (0, 0, 0), 2 )
    return ny_cont


def get_center(contur):
    center = cv2.moments(contur)
    x = int(center["m10"] / center["m00"])
    y = int(center["m01"] / center["m00"])
    return (x,y)


def calc_distance(centers, focal_len, camera_space):
    dist = abs(centers[0][0]-centers[1][0])
    if dist == 0:
        return 50
    return int((3.631e-6 * (dist**4)) - (0.003035 * (dist**3)) + (0.9672 * (dist**2)) - (139.9 * dist) + 7862)
    #return int(((focal_len*camera_space)/dist)*100)


def calc_size(num_pixels:int, centers, axis:int=0):
    """Calculates size with center points and number of pixelse size of object, axis=0 refers to horisontal measurment"""
    factor = -0.002344
    constant = 0.541
    dist = abs(centers[0][0]-centers[1][0])
    #print(f'Distance between pic: {dist}, Object size: {num_pixels}')
    return round((dist * factor + constant)*num_pixels, 1)


if __name__ == "__main__":
    camera(2)
