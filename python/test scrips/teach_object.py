import cv2
import os
import numpy as np

def teach(path, name):
    with open(f'{name}.txt','r') as fil:
        f = open()
        for a in os.listdir(path):
            bilde = cv2.imread(a)
            hoyde, bredde, chr = bilde.shape
            f.write(f'{path}/{a}.png 1 0 0 {hoyde} {bredde}')a