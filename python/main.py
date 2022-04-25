import multiprocessing
from multiprocessing.dummy import Array
from mercury import Mercury
from mercury import venus
from theia import Theia
import time
import threading
import json

# Our main loop for both programs
def main_loop():
    m = Mercury()
    m.thei.toggle_front()
    m.thei.toggle_back()

    while(1):
        for _ in range(4):
            time.sleep(0.7)
            print("Still running.  ", end='\r')
            time.sleep(0.7)
            print("Still running.. ", end='\r')
            time.sleep(0.7)
            print("Still running...", end='\r')

if __name__ == "__main__":
    main_loop()