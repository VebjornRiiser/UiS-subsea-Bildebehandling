1#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import struct
import threading
import time
import serial
import socket
import json
from network_handler import Network
from theia import Theia

c_types = {
    "int8": "<b",
    "uint8": "<B",
    "int16": "<h",
    "uint16": "<H",
    "int32": "<i",
    "uint32": "<I",
    "int64": "<q",
    "uint64": "<Q",
    "float": "<f"
}

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
    print("test")
    flag['network'] = True
    while flag['network']:
        try:
            melding = network_handler.receive()
            #melding = network_socket.recv(1024) #  OLD
            if melding == b"" or melding is None:
                continue
            else:
                print(melding)
                #network_callback(melding)
        except ValueError as e:
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
            #print(melding)
            USB_callback(melding)
        except Exception as e:
            print(e)
            pass
    print("USB thread stopped")

# Only handles CAN messages, expecting messages to be tuples with length 2, where index 0 is can ID, and index 1 is the datapackage.
def create_json(can_id:int, data:str):
    if len(data) != 32:
        return False
    
    # Python....
    data_b = data.encode('latin').decode('unicode_escape').encode('latin')
    
    # Leak detection and temperature
    if can_id == 140:
        lekk = data_b[0]
        temp1 = struct.unpack(c_types["int16"], data_b[1:3])[0] / 10 # -100.0°C -> 100.0°C
        temp2 = struct.unpack(c_types["int16"], data_b[3:5])[0] / 10
        temp3 = struct.unpack(c_types["int16"], data_b[5:7])[0] / 10
        json_dict = {"sensor1": [lekk, temp1, temp2, temp3 ]}
        
    return json.dumps(json_dict)
        

def intern_com_thread(intern_com, intern_com_callback, flag):
    print("Starting internal communication")
    flag['intern'] = True
    while flag['intern']:
        data = intern_com.recv()
        intern_com_callback(data)


class Mercury:
    def __init__(self, ip:str="0.0.0.0", port:int=6900) -> None:
        # Flag dictionary
        self.status ={'network': False, 'USB': False, 'intern': False}
        self.connect_ip = ip
        self.connect_port = port
        self.net_init()
        self.thei = Theia()

        # USB socket
        self.serial_port = "/dev/ttyACM0"
        self.serial_baud = 9600
        if not self.status['USB']:
            self.toggle_USB()
        #self.network_snd_socket.send_string(f'USB connection started')


    def net_init(self):
        self.network_handler = Network(is_server=True, bind_addr=self.connect_ip, port=self.connect_port)
        while self.network_handler.waiting_for_conn:
            time.sleep(0.3)
            print("waiting for connection before continuing")
        self.toggle_network()

        ##### OLD
        #self.network_rcv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #self.network_rcv_socket.bind((self.connect_ip, self.connect_port))
        #self.network_rcv_socket.listen()
        #self.network_connection, self.network_address = self.network_rcv_socket.accept()


    def network_callback(self, data: bytes) -> None:
        for message in data.split("*"):
            if message == b'heartbeat':
                continue
            else:
                if isinstance(message, list):
                    return
                message = json.loads(message)
                for item in message:
                    if item[0] < 500:
                        if self.status['USB']:
                            self.serial.write(serial_package_builder())
                        else:
                            self.network_handler.send(create_json('error', 15149))
                    else:
                        if isinstance(item[1], str):
                            if item[1].lower() == "tilt":
                                pass
                            elif item[1].lower() == "toggle_front":
                                answ = self.thei.toggle_front()
                                if not answ:
                                    self.network_handler.send(create_json('error', 15152))
                        else:
                            print(item[1])


    def toggle_network(self):
        if self.status['network']:
            # This will stop network thread
            self.status['network'] = False
        else:
            self.network_trad = threading.Thread(name="Network_thread",target=network_thread, daemon=True, args=(self.network_handler, self.network_callback, self.status))
            self.network_trad.start()
            
    def USB_callback(self, melding):
        if self.status['network']:
            data, can_id = melding.split(";")
            self.network_handler.send(bytes(create_json(int(can_id), data), 'utf-8'))
        else: 
            print('No connection on network')


    def toggle_USB(self):
        if self.status['USB']:
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
