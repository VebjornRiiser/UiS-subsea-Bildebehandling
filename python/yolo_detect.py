from calendar import c
from operator import pos
import cv2
from sys import platform
import numpy as np
import time
import torch
from models.common import DetectMultiBackend
from utils.datasets import IMG_FORMATS, VID_FORMATS, LoadImages, LoadStreams
from utils.general import (LOGGER, check_file, check_img_size, check_imshow, check_requirements, colorstr,
                           increment_path, non_max_suppression, print_args, scale_coords, strip_optimizer, xyxy2xywh)
from utils.plots import Annotator, colors, save_one_box
from utils.torch_utils import select_device, time_sync
from utils.augmentations import letterbox


class Yolo(): # 
    def __init__(self, resol, name:str = 'Rubberfish') -> None:
        self.device = select_device('') # Finds possible hardware to use
        print(self.device)
        self.weights = 'models/best.pt' # Used machine learning
        self.data = 'data/coco128.yaml' 
        self.conf_trees = 0.80 # How high confedence we want for a match
        self.iou_tres = 0.45 
        self.color = (255, 0, 0) # Color for frames drawn around object
        self.text = name # Text drawn on picture
        self.model = DetectMultiBackend(self.weights, self.device, False, self.data,)
        imgsz=[640, 640] # Size of pic samples
        self.resolution = resol # Image resolution
        self.imgsz = check_img_size(imgsz, s=self.model.stride)
        tride, names, pt, jit, onnx, engine = self.model.stride, self.model.names, self.model.pt, self.model.jit, self.model.onnx, self.model.engine
        if pt or jit:
            self.model.model.float()
        self.model.warmup(imgsz=(1, 3, *imgsz), half=False)
        self.resize = [float(resol[1])/384, float(resol[0])/640]

    def yolo_image(self, image, test = False): #Find shapes using YOLO (Mostly fish)
        shape = image.shape
        gn = torch.tensor(image.shape)[[1, 0, 1, 0]]  # normalization gain whwh
        image = letterbox(image, self.imgsz, stride=self.model.stride, auto=True)[0]
        image = image.transpose((2, 0, 1))[::-1] # Transpose picture from BGR to RGB, torch needs RGB
        image = np.ascontiguousarray(image) # Numpy magic
        image = torch.from_numpy(image).to(self.device) # Everything is faster with torch
        image = image.float() # Float to later devide color data
        image /= 255
        if len(image.shape) == 3: 
            image = image[None] # Adds element to start of list
        pred = self.model(image, augment=False, visualize=False)
        pred = non_max_suppression(pred, self.conf_trees)
        detected_list = []
        for i, detected in enumerate(pred):
            for *xyxy, conf, cls in reversed(detected):
                #print(xyxy)
                wx = (torch.tensor(xyxy).view(1, 4))
                wx = self.resize_square(wx[0])
                detected_list.append(Object(wx,self.text, self.color, conf))
                #print(len(wx[0]))
                # print(f'{float(conf)}\n')
                #xywh = (xyxy2xywh(torch.tensor(xyxy).view(1, 4)) / gn).view(-1).tolist()
                #print(xyxy[:,0])
        return detected_list


    def resize_square(self, xyxy:list):
        xyxy = xyxy.numpy()
        c = 1
        for a, b in enumerate(xyxy):
            xyxy[a] = b*self.resize[c]
            c += 1
            if c > 1:
                c = 0
        return xyxy

def camera(camera_id): #Testfunction to get images from camera
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
    yal = Yolo((frame_width, frame_height))
    if not (feed.isOpened()):
        print("Could not open video device")
        run = False
    total_list = []
    while run:
        ref, frame = feed.read()
        if ref:
            detected_stuff = yal.yolo_image(frame)
            if len(detected_stuff):
                for item in detected_stuff:
                    cv2.rectangle(frame, item.rectangle[0], item.rectangle[1], item.colour, item.draw_line_width)
                    cv2.putText(frame, item.name, (item.rectangle[0][0], item.rectangle[0][1]+40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 3)
                    cv2.putText(frame, item.name, (item.rectangle[0][0], item.rectangle[0][1]+40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 1)
        cv2.imshow("Named Frame",frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    feed.release()
    cv2.destroyAllWindows()



class Object(): # Used in functions to draw on image, find distance to objects etc, refers to objects in pictures
    def __init__(self, xyxy:list, name:str, colour:tuple, confidence:float) -> None:
        self.rectangle = [(int(xyxy[0]), int(xyxy[1])), (int(xyxy[2]), int(xyxy[3]))]
        self.angle = 0
        self.box = 0 #[np.int0(cv2.boxPoints(self.rectanlge))] # Added into a list due to easier use in draw contours
        self.width = (self.rectangle[0][1] - self.rectangle[0][0])/2 # Calulates and set width
        self.height = (self.rectangle[1][1] - self.rectangle[1][0])/2 # Calulates and set height
        self.position = (self.rectangle[0][0] + self.width, self.rectangle[1][0] + self.height) # Calulates and set center
        self.true_width = 0 # Needs to be calulated using another picture and compare positions
        self.areal = self.width*self.height
        self.dept = 0
        self.name = f'{name}, confidence:{round(float(confidence.cpu().numpy()), 2)}'
        self.draw_line_width = 2
        self.colour = colour
        self.confidence = confidence

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
    def get_dept(self):
        return self._dept

    def set_dept(self, newdept):
        self._dept = newdept

    @property
    def get_true_width(self):
        return self._true_width

    def set_true_width(self, newwidth):
        self._true_width = newwidth

if __name__ == "__main__":
    camera(2)
