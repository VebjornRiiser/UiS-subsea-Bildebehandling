import multiprocessing
from multiprocessing.dummy import Array
from mercury import Mercury
from mercury import venus
from theia import Theia
import time
import threading
import json

import logging

# setter opp logging


def generate_logging(log_name: str = "Hovedlogger"):
    logging.basicConfig(level=logging.NOTSET) #setter hovedloggeren til det laveste nivået
    main_logger = logging.getLogger(log_name)

    return main_logger

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