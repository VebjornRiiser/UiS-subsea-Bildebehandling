1#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from doctest import ELLIPSIS_MARKER
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

def can_handler_up(id, msg):
    print(f'Can Id:{id}, Data:{msg}')
    if int(id) == 80:
        print(f'Can Id:{id}, Data:{msg}')
    else:
        pass

def get_byte(c_format:str, number):
    byte_list = []
    [byte_list.append(i) for i in struct.pack(c_types[c_format], number)]

    return byte_list


def serial_package_builder(data, can=True):
    package = []
    # can_data is a list or a dict
    can_id, can_data = data

    # Start byte
    package.append(0x02)

    # CAN eller kamera tilt
    package.append(0x05) if can else package.append(0x06)

    # ID
    package += get_byte("uint8", can_id)
    
    # Startup
    if (can_id == 64) | (can_id == 96) | (can_id == 128):
        package += bytes("start\n", "latin")
        for k in range(2):
            package.append(0x00)

    elif can_id == 70:
        # X, Y, Z, rotasjon: int8
        for k in range(4):
            package += get_byte("int8", can_data[k])

        # manipulator: uint8
        package += get_byte("uint8", can_data[4])

        # fri, fri, throttling: int8
        for k in range(3):
            package += get_byte("int8", can_data[k+5])
    
    # Camera tilt
    elif (can_id == 200) | (can_id == 201):
        package += get_byte("int8", can_data['tilt'])
        for _ in range(7):
            package.append(0x00)

    else:
        return f"Gjenkjente ikkje ID frå toppside: '{can_id}'"



    # Info om struct: https://docs.python.org/3/library/struct.html

    # Slutt byte
    package.append(0x03)

    if len(package) == 12:
        try:
            return bytearray(package)
        except ValueError:
            return f"feil lengde på tall: '{package}'"
    else:
        return f"Feil lengde på liste: '{package}'"

# Reads data from network port
def network_thread(network_handler, network_callback, flag):
    print("Server started\n")
    flag['network'] = True
    while flag['network']:
        try:
            melding = network_handler.receive()
            #melding = network_socket.recv(1024) #  OLD
            if melding == b"" or melding is None:
                continue
            else:
                #print(melding)
                network_callback(melding)
        except ValueError as e:
            print(f'Feilkode i network thread feilmelding: {e}\n\t{melding = }')
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
            print(f'Feilkode i usb thread feilmelding: {e}')
            pass
    print("USB thread stopped")

# Only handles CAN messages, expecting messages to be tuples with length 2, where index 0 is can ID, and index 1 is the datapackage.
def create_json(can_id:int, data:str):
    if len(data) != 32:
        return to_json(False)
    
    # Python....
    data_b = data.encode('latin').decode('unicode_escape').encode('latin')
    
    # Leak detection and temperature
    if can_id == 140:
        lekk = data_b[0]
        temp1 = struct.unpack(c_types["int16"], data_b[1:3])[0] / 10 # -100.0°C -> 100.0°C
        temp2 = struct.unpack(c_types["int16"], data_b[3:5])[0] / 10
        temp3 = struct.unpack(c_types["int16"], data_b[5:7])[0] / 10
        json_dict = {"sensor1": [lekk, temp1, temp2, temp3 ]}
    else:
        json_dict = "\n\nERROR, ID UNKNOWN!\n\n"    

    return to_json(json_dict)


def to_json(input):
    packet_sep = json.dumps("*")
    
    return bytes(packet_sep + json.dumps(input) + packet_sep, "utf-8")


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

    def network_callback(self, data: bytes) -> None:
        data:str = bytes.decode(data, "utf-8")
        for message in data.split( json.dumps("*") ):
            #print(f'Sjekker for heartbeat {data = }, {message = }')
            if message == json.dumps('heartbeat') or message == "":
                continue
            else:
                message = json.loads(message)
                for item in message:
                    if item[0] < 200:
                        print(message)
                        if self.status['USB']:
                            self.serial.write(serial_package_builder(item))
                        else:
                            self.network_handler.send(to_json("error usb not connected"))
                    elif (item[0] == 200) | (item[0] == 201): #Camera_front and back functions
                        #key = item[1]
                        print(item[1])
                        for key in item[1]:
                            if key.lower() == "tilt":
                                print("Test print 204")
                                if self.status['USB']:
                                    mld = serial_package_builder(item, False)
                                    if not isinstance(mld, bytearray):
                                        self.network_handler.send(to_json(f'{mld}'))
                                    else:
                                        if not self.thei.camera_function['front'] and item[0] == 200:
                                            self.serial.write(mld)
                                        elif not self.thei.camera_function['back'] and item[0] == 201:
                                            self.serial.write(mld)
                                        else:
                                            self.network_handler.send(to_json("Video prossesing running, cant tilt camera"))
                                else:
                                    self.network_handler.send(to_json("error usb not connected"))
                            elif key.lower() == "on":
                                if item[0] == 200:
                                    print("toggle front")
                                    answ = self.thei.toggle_front()
                                elif item[0] == 201:
                                    print("toggle back")
                                    answ = self.thei.toggle_back()
                                else:
                                    self.network_handler.send(to_json("Invalid camera")) # Not possible to send this in theroy
                                if not answ:
                                    self.network_handler.send(to_json("Could not find front camera"))
                            elif key.lower() == "bildebehandligsmodus":
                                if item[0] == 200:
                                    if item[1][key] != 0:
                                        self.thei.camera_function['front'] = True
                                        mld = serial_package_builder(self.thei.set_front_zero)
                                        self.serial.write(mld)
                                    else:
                                        self.thei.camera_function['front'] = False
                                    if self.thei.camera_status['front']:
                                        self.thei.host_cam_front.send(item[1][key])
                                    else:
                                        self.network_handler.send(to_json("Front camera is not on"))
                                elif item[0] == 201:
                                    if item[1][key] != 0:
                                        self.thei.camera_function['back'] = True
                                        mld = serial_package_builder(self.thei.set_back_zero)
                                        self.serial.write(mld)
                                    else:
                                        self.thei.camera_function['back'] = False
                                    if self.thei.camera_status['back']:
                                        self.thei.host_back.send(item[1][key])
                                    else:
                                        self.network_handler.send(to_json("Back camera is not on"))
                    else:
                        self.network_handler.send(to_json("This ID is not handled"))

    def toggle_network(self):
        if self.status['network']:
            # This will stop network thread
            self.status['network'] = False
        else:
            self.network_trad = threading.Thread(name="Network_thread",target=network_thread, daemon=True, args=(self.network_handler, self.network_callback, self.status))
            self.network_trad.start()
        
    def USB_callback(self, melding):
        if melding == "":
            return

        if self.status['network']:
            #print(f"usb callback {melding =}")
            data, can_id = melding.split(";")
            can_handler_up(can_id, data)
            self.network_handler.send(create_json(int(can_id), data))
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
    a.thei.toggle_front()
    #a.thei.toggle_back()
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
