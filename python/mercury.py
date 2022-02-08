1#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ast import Bytes
import struct
import threading
import time
#import serial
import socket
import json
from network_handler import Network
from theia import Theia


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
    network_socket.close()

#!TODO packaged builder for sending of serial data
def serial_package_builder(data, can):
    package = []
    # Start byte
    package.append(0x02)

    # CAN eller kamera tilt
    package.append(0x05) if can else package.append(0x06)

    # ID
    [package.append(i) for i in struct.pack('<B', data[0])]

    # 8 Byte CAN Data
    if data[0] == 59:
        for char in data[1]:
            package.append(ord(char))
        #[package.append(i) for i in struct.pack('<B',ord(data[1]))]
    elif data[0] == 70:
        pass
        #[package.append(i) for i in struct.pack('<B', data[1])]


    #TODO Lage til alle typer data som skal mottas: https://docs.python.org/3/library/struct.html
    #[package.append(i) for i in struct.pack('<q', 345)]

    # Slutt byte
    package.append(0x03)

    return bytearray(package)

# Reads data from network port
def network_thread(network_handler, network_callback, flag):
    print("Server started\n")
    flag['network'] = True
    while flag['network']:
        try:
            melding = network_handler.receive()
            #melding = network_socket.recv(1024) #  OLD
            if melding == b"":
                break
            else:
                print(melding)
                network_callback(melding)
        except Exception as e:
            print(e)
            print("Exception")
            break
    network_handler.exit()
    print(f'Network thread stopped')

# Reads serial data
def USB_thread(h_serial, USB_callback, flag):
    flag['USB'] = True
    while flag['USB']:
        try:
            melding = h_serial.readline().decode("utf8").strip("\n")
            USB_callback(melding)
        except Exception as e:
            print(e)
            pass
    print("USB thread stopped")

# Only handles CAN messages, expecting messages to be tuples with length 2, where index 0 is can ID, and index 1 is the datapackage.
def create_json(index:str, data):
    dict = {index:data}
    return json.dumps(dict)
        

def intern_com_thread(intern_com, intern_com_callback, flag):
    print("Starting internal communication")
    flag['intern'] = True
    while flag['intern']:
        data = intern_com.recv()
        intern_com_callback(data)


class Mercury:
    def __init__(self, ip:str="0.0.0.0", port:int=6900) -> None:
        # Flag dictionary
        self.status ={'network':False, 'USB':False, 'intern':False}
        self.connect_ip = ip
        self.connect_port = 6969
        self.net_init()
        self.thei = Theia()

        # USB socket
        self.serial_port = "/dev/ttyACM0"
        self.serial_baud = 9600
        if self.status['USB']:
            self.toggle_USB()
        #self.network_snd_socket.send_string(f'USB connection started')


    def net_init(self):
        self.network_handler = Network(is_server=True, bind_addr=self.connect_ip, port=self.connect_port)
        self.toggle_network()

        ##### OLD
        #self.network_rcv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #self.network_rcv_socket.bind((self.connect_ip, self.connect_port))
        #self.network_rcv_socket.listen()
        #self.network_connection, self.network_address = self.network_rcv_socket.accept()


    def network_callback(self, message: Bytes):
        message = json.loads(message.decode())
        for key in message:
            if key.lower() == "can":
                if self.status['USB']:
                    for item in message[key]:
                        #print(serial_package_builder(item, True))
                        self.serial.write(serial_package_builder(item, True))
                    else:
                        self.network_handler.send(create_json('error', 15150))
            elif key.lower() == "tilt":
                if self.status['USB']:
                    pass
                    self.serial.write(serial_package_builder(item, False))
                    print("TILT")
                else:
                    self.network_handler.send(create_json('error', 15151))
                    #self.network_handler.
            elif key.lower() == "camera":
                for item in message[key]:
                    if item == 'toggle_front':
                        answ = self.thei.toggle_front()
                        if not answ:
                            self.network_handler.send(create_json('error', 15152))


    def toggle_network(self):
        if self.status['network']:
            # This will stop network thread
            self.status['network'] = False
        else:
            self.network_trad = threading.Thread(name="Network_thread",target=network_thread, daemon=True, args=(self.network_handler, self.network_callback, self.status)).start()

    def USB_callback(self, melding):
        if self.status['network']:
            self.network_handler.send(bytes(melding, 'utf-8'))
        else: print('No connection on network')


    def toggle_USB(self):
        if self.USB_status:
            # This will stop USB thread
            self.status['USB'] = False
            time.sleep(2)
            self.serial.close()
        else:
            self.serial = serial.Serial(self.serial_port, self.serial_baud, timeout=1)
            self.serial.write(b"t")
            self.serial_thread = threading.Thread(name = "Serial_thread", target=USB_thread, daemon=True, args=(self.serial, self.USB_callback, self.status)).start()

            

if __name__ == "__main__":
    print(f'Mercury')
    a = Mercury()
    #dictionary = {"CAN":1, "camera": 1}
    #ip = "127.0.0.1"
    #port = 6900
    #venus_trad = threading.Thread(name="venus", target=venus, args=(ip, port, meld))
    #venus_trad.start()
    #a = Mercury()
    #a.toggle_network()
    #print("For loop started")
    for __ in range(200):
        time.sleep(5)
