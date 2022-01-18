#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from ast import arg
from contextvars import Context
from json.tool import main
from mimetypes import init
from multiprocessing import context
import struct
from unicodedata import name
from xml.etree.ElementInclude import include
import threading
#import cv2
import time
#import serial
import socket
import json

# Test function for socket connection
def venus(ip, port, meld):
    network_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    network_socket.settimeout(3)
    network_socket.connect((ip, port))
    for __ in range(10):
        time.sleep(0.2)
        try:
            network_socket.sendall(str.encode(meld))
        except Exception as e:
            print(e)
            print("Connection lost")
            break
    time.sleep(5)
    print("test")
    network_socket.close()

#!TODO packaged builder for sending of serial data
def serial_package_builder(data, can):
    package = []
    param_bin = 0b00000000
    
    package.append(0x02)
    package.append(0x05) if can else package.append(0x06)
    package.append(param_bin)

    #TODO Lage til alle typer data som skal mottas: https://docs.python.org/3/library/struct.html
    [package.append(i) for i in struct.pack('<q', 345)]

    package.append(0x03)

    return bytearray(package)

# Reads data from network port
def network_thread(network_socket, network_callback, flag):
    print("Server started\n")
    while flag[0]:
        try:
            melding = network_socket.recv(1024)
            if melding == b"":
                break
            else:
                network_callback(melding)
        except:
            print("Exception")
            break
    network_socket.close()
    print(f'Thread stopped')

# Reads serial data
def USB_thread(h_serial, USB_callback, flag):
    while flag[1]:
        try:
            melding = h_serial.readline().decode("utf8").strip("\n")
            USB_callback(melding)
        except:
            pass
    print("USB thread stopped")

def intern_com_thread(intern_com, intern_com_callback, flag):
    print("Starting internal communication")
    while (flag[2]):
        data = intern_com.recv()
        intern_com_callback(data)
class Mercury:
    def __init__(self) -> None:
        # Flags
        self.network_status = False
        self.USB_status = False
        self.status_flag_list = [1,1,1,1,1] # Index 0 = Network, Index 1 = USB, Index 3 = Intern com, index 4 = ?
        self.connect_ip = "0.0.0.0"
        self.connect_port = 6900
        self.net_init()

        # USB socket
        self.serial_port = "/dev/ttyACM0"
        self.serial_baud = 9600
        #self.toggle_USB()
        #self.network_snd_socket.send_string(f'USB connection started')


    def net_init(self):
        self.network_rcv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.network_rcv_socket.bind((self.connect_ip, self.connect_port))
        #self.network_rcv_socket.settimeout(20)
        self.network_rcv_socket.listen()
        self.network_connection, self.network_address = self.network_rcv_socket.accept()


    def network_callback(self, message):
        message = json.loads(message.decode())
        for key in message:
            if key.lower() == "can" or key.lower() == "tilt":
                self.serial.write(serial_package_builder(message[key], True if key.lower() == "can" else False))
                print("CAN")
            elif key.lower() == "camera":
                print("camera")
            else:
                print("Failed")


    def toggle_network(self):
        if self.network_status:
            self.status_flag_list = 0
            self.network_status = False
        else:
            print("Starting thread")
            self.network_trad = threading.Thread(name="Network_thread",target=network_thread, daemon=True, args=(self.network_connection, self.network_callback, self.status_flag_list))
            self.network_trad.start()
            self.network_status = True

    def USB_callback(self, melding):
        self.network_snd_socket(melding)


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
    #dictionary = {"CAN":1, "camera": 1}
    #meld = json.dumps(dictionary)
    #ip = "127.0.0.1"
    #port = 6900
    #venus_trad = threading.Thread(name="venus", target=venus, args=(ip, port, meld))
    #venus_trad.start()
    #a = Mercury()
    #a.toggle_network()
    #print("For loop started")
    #for __ in range(20):
    #    time.sleep(5)
    #print("For loop stopped")