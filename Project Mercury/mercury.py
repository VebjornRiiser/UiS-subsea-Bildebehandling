#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from json.tool import main
from mimetypes import init
from multiprocessing import context
from unicodedata import name
#from socket import socket
#from socket import socket
from xml.etree.ElementInclude import include
import threading
import cv2
import zmq
import time
import serial

def mercury():
    #init
    context = zmq.Context()
    network_socket = context.socket(zmq.REQ)
    network_socket.connect("tcp://127.0.0.1:6892")
    while True:
        network_socket.send(b'TEST')
        break


def network_thread(network_socket, network_callback, flag):
    network_socket.bind("tcp://127.0.0.1:6892")
    while flag[0]:
        melding = network_socket.recv()
        print(melding)
        network_callback(melding)
        break
    time.sleep(5) #!TODO! REMOVE AFTER TEST
    network_callback(melding)
    print(f'Thread stopped')

def USB_thread():
    pass

class Callbacks:
    def __init__(self) -> None:
        # Flags
        self.network_status = False
        self.USB_status = False
        self.status_flag_list = [1,1,1,1,1] # Index 0 = Network, Index 1 = USB, Index 3 = ?, index 4 = ?

        # Network socket
        context = zmq.Context()
        self.network_socket = context.socket(zmq.REP)

        # USB socket
        self.serial_port = "COM1"
        self.serial_baud = 9600

    def network_callback(self, message):
        if message[0] == "CAN":
            self.send_can(message)
        elif message[0] == "kamera":
            #Kjor kamerafunksjon
            pass
        else:
            print("Called back\n")
            self.send_can(message)
        
    def toggle_network(self):
        if self.network_status:
            self.status_flag_list = 0
            self.network_status = False
        else:
            self.network_trad = threading.Thread(name="Network_thread",target=network_thread, daemon=True, args=(self.network_socket, self.network_callback, self.status_flag_list))
            self.network_trad.start()
            self.network_status = True

    def USB_callback():
        pass

    def toggle_USB(self):
        if self.USB_status:
            self.status_flag_list[1] = 0
            self.USB_status = False
        else:
            self.serial = serial.Serial(self.serial_port, self.serial_baud, timeout=1)
            self.serial_thread = threading.Thread(name = "Serial_thread", target=USB_thread, daemon=True, args=(self.USB_callback, self.serial, self.status_flag_list))
            self.network_trad.start()
            self.USB_status = True

    def send_can(self, message):
        print(message)



if __name__ == "__main__":
    a = Callbacks()
    a.toggle_network()
    mercury()
    a = 1
    while True:
        time.sleep(1)
        a += 1
        if a > 10:
            break