#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import struct
import threading
import time
import serial
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
def network_thread(network_socket, network_callback, flag):
    print("Server started\n")
    while flag[0]:
        try:
            melding = network_socket.recv(1024)
            if melding == b"":
                break
            else:
                network_callback(melding)
        except Exception as e:
            print(e)
            print("Exception")
            break
    network_socket.close()
    print(f'Network thread stopped')

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
    def __init__(self, ip:str="10.0.0.3", port:int=6900) -> None:
        # Flags
        self.network_status = False
        self.USB_status = False
        self.status_flag_list = [1,1,1,1,1] # Index 0 = Network, Index 1 = USB, Index 3 = Intern com, index 4 = ?
        self.connect_ip = ip
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
        self.network_rcv_socket.listen()
        self.network_connection, self.network_address = self.network_rcv_socket.accept()


    def network_callback(self, message):
        message = json.loads(message.decode())
        for key in message:
            if key.lower() == "can":
                for item in message[key]:
                    print(serial_package_builder(item, True))
            elif key.lower() == "tilt":
                pass
                #self.serial.write(serial_package_builder(message[key], True if key.lower() == "can" else False))
                print("TILT")
            elif key.lower() == "camera":
                pass
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
        print(melding)
        #self.network_snd_socket(melding)


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
    pass
    #dictionary = {"CAN":1, "camera": 1}
    #ip = "127.0.0.1"
    #port = 6900
    #venus_trad = threading.Thread(name="venus", target=venus, args=(ip, port, meld))
    #venus_trad.start()
    #a = Mercury()
    #a.toggle_network()
    #print("For loop started")
    #for __ in range(20):
    #    time.sleep(5)