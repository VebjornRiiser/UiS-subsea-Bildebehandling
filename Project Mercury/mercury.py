#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from json.tool import main
from mimetypes import init
from multiprocessing import context
from unicodedata import name
from xml.etree.ElementInclude import include
import threading
#import cv2
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

# Reads data from network port
def network_thread(network_socket, network_callback, flag):
    network_socket.bind("tcp://127.0.0.1:6892")
    while flag[0]:
        melding = network_socket.recv()
        network_callback(melding)
    print(f'Thread stopped')

# Reads serial data
def USB_thread(h_serial, USB_callback, flag):
    #h_serial.write(b"ds")
    
    while flag[1]:
        melding = h_serial.readline().decode("utf8").strip("\n")
        USB_callback(melding)
    print("USB thread stopped")

class Callbacks:
    def __init__(self) -> None:
        # Flags
        self.network_status = False
        self.USB_status = False
        self.status_flag_list = [1,1,1,1,1] # Index 0 = Network, Index 1 = USB, Index 3 = ?, index 4 = ?

        # Network socket recive
        context = zmq.Context()
        self.network_rcv_socket = context.socket(zmq.REP)

        # Network socket send
        context2 = zmq.Context()
        self.network_snd_socket = context.socket(zmq.REQ)
        # Waiting for TOPSIDE
        #self.network_snd_socket.connect("tcp://10.0.0.1:6899")

        # USB socket
        self.serial_port = "/dev/ttyACM0"
        self.serial_baud = 9600
        self.toggle_USB()
        self.network_snd_socket.send_string(f'USB connection started')

    def network_callback(self, message):
        self.serial.write(message)
        
    def toggle_network(self):
        if self.network_status:
            self.status_flag_list = 0
            self.network_status = False
        else:
            self.network_trad = threading.Thread(name="Network_thread",target=network_thread, daemon=True, args=(self.network_socket, self.network_callback, self.status_flag_list))
            self.network_trad.start()
            self.network_status = True

    def USB_callback(self, melding):
        #self.network_snd_socket(melding)
        print(melding)

    def toggle_USB(self):
        if self.USB_status:
            self.status_flag_list[1] = 0
            time.sleep(2)
            self.serial.close()
            self.USB_status = False
        else:
            self.serial = serial.Serial(self.serial_port, self.serial_baud, timeout=1)
            self.serial.write(b"t")
            self.serial_thread = threading.Thread(name = "Serial_thread", target=USB_thread, daemon=True, args=(self.serial, self.USB_callback, self.status_flag_list))
            self.serial_thread.start()
            self.USB_status = True


if __name__ == "__main__":
    a = Callbacks()
    #a.toggle_network()
    #mercury()
    while True:
        time.sleep(1)