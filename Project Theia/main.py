from ctypes import sizeof
from json.tool import main
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


def waitfunk(sleep):
    print("test")
    a = 0
    while a < 100:
        a += 1
        print(a)
        time.sleep(sleep)


if __name__ == "__main__":
    context = zmq.Context()
    video_source = context.socket(zmq.PAIR)
    camera_prossess = multiprocessing.Process(target=camera, args=(0,))
    wait_prossess = multiprocessing.Process(target=waitfunk, args=(1,))
    camera_prossess.start()
    wait_prossess.start()
