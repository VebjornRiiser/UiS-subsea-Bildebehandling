import multiprocessing
from multiprocessing.dummy import Array
from mercury import Mercury
from mercury import venus
from theia import Theia
import time
import threading
import json
from logging_init import generate_logging
import logging

# setter opp logging




# Our main loop for both programs
def main_loop():
    
    m = Mercury(logger=generate_logging()) #WARNING Dette er ikke sikker fungerer
    m.thei.toggle_front()
    m.thei.toggle_back()

    while(1):
        time.sleep(2)
        print("Still running")

if __name__ == "__main__":
    main_loop()