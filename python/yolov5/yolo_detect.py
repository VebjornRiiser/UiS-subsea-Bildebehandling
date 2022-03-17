from operator import pos
import cv2
from sys import platform
import numpy as np
import time
import torch
from yolov5.models.common import DetectMultiBackend
from yolov5.utils.datasets import IMG_FORMATS, VID_FORMATS, LoadImages, LoadStreams
from yolov5.utils.general import (LOGGER, check_file, check_img_size, check_imshow, check_requirements, colorstr,
                           increment_path, non_max_suppression, print_args, scale_coords, strip_optimizer, xyxy2xywh)
from yolov5.utils.plots import Annotator, colors, save_one_box
from yolov5.utils.torch_utils import select_device, time_sync



class Yolo():
    def __init__(self) -> None:
        self.device = select_device('')
        self.weights = '/yolov5/models/yolov5s.pt'
        self.data = '/yolov5/data/coco128.yaml'
        self.conf_trees = 0.25
        self.iou_tres 
        self.model = DetectMultiBackend(self.weights, self.device, False, self.data)
        self.model.warmup((1, 3, 1280, 960)) # Tage u fix, ikkje sikker ka me sga her

    def yolo_image(self, image, test = False): #Find shapes using YOLO (Mostly fish)
        image = torch.from_numpy(image).to(self.device)
        image = image.float()
        image /= 255
        if len(image.shape) == 3: # What this does it not clear
            image = image[None]
        pred = self.model(image, False, False)
        pred = non_max_suppression(pred, self.conf_trees)
        for i, detected in enumerate(pred):
            print("Deteced object\n")
            print(detected)
        if test:
            cv2.imshow('WindowName', image)

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
    if not (feed.isOpened()):
        print("Could not open video device")
        run = False
    total_list = []
    while run:
        ref, frame = feed.read()
        crop_frame = frame[:frame_height, :crop_width]
        crop_frame2 = frame[:frame_height,crop_width:]
        cv2.imshow("Named Frame",crop_frame)
        cv2.imshow("named Frame2", crop_frame2)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    feed.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    camera(2)
