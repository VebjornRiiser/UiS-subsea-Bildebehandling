from ctypes import sizeof
from json.tool import main
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




def camera(camera_id):
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


def waitfunk(sleep:int=100) -> None: 
    """Wait function that prints a value before it sleeps for a given time

    Args:
        sleep (int, optional): Time given in sekunds, waits sleep*100. Defaults to 100.
    """
    print("test")
    a = 0
    while a < 100:
        a += 1
        print(a)
        time.sleep(sleep)


#TODO cli_runtime
#Funksjon som håndterer en commandline interface for prossesser (slik at man kan styre ting når man tester)
# Denne skulle kanskje vært en toggle funksjon som man kan enable fra click når man kjører programmet


def cli_runtime():
    
    pass
 
 
#INFO https://docs.opencv.org/4.x/d8/dfe/classcv_1_1VideoCapture.html
# Bruke grap og retrive når man bruker flere kameraer (Er vist den riktige måten å gjøre det på)



if __name__ == "__main__":
    context = zmq.Context()
    video_source = context.socket(zmq.PAIR)
    camera_prossess = multiprocessing.Process(target=camera, args=(0,))
    camera_prossess2 = multiprocessing.Process(target=camera, args=(1,))
    wait_prossess = multiprocessing.Process(target=waitfunk, args=(1,))
    
    wait_prossess2 = multiprocessing.Process(target=waitfunk, args=(1,))
    #camera_prossess.start()
    #camera_prossess2.start()
    wait_prossess.start()
    wait_prossess2.start()

