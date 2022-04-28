import threading
import socket
import sys
import time
import json
import subprocess

# global local
# local = False
# if len(sys.argv) > 1:
#     if sys.argv[1] == "True":
#         local = True


class Network:
    # bind_addr needs to be set if is_server is false and connect_addr needs to be set if is_server is false  
    def __init__(self, is_server=False, bind_addr="127.0.0.1", port=6900, connect_addr="127.0.0.1"):
        self.is_server = is_server
        self.bind_addr = bind_addr
        self.connect_addr = connect_addr
        self.port = port
        self.waiting_for_conn = True
        self.conn = None
        self.running = True
        self.timeout = -1

        self.new_conn()
        self.heartbeat = threading.Thread(target=self.beat, daemon=True)
        self.heartbeat.start()

    def beat(self):
        while self.running:
            heartbeat_packet = bytes(json.dumps("*"), "utf-8") + bytes(json.dumps("heartbeat"), "utf-8") + bytes(json.dumps("*"), "utf-8")
            self.send(heartbeat_packet)
            time.sleep(0.3)

    def new_conn(self):
        self.conn = None
        self.waiting_for_conn = True
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if not self.running:
            return
        if self.is_server:
            print(f"trying to bind with {self.bind_addr, self.port}")
            self.socket.bind((self.bind_addr, self.port))
            self.socket.listen()
            print("starting wait for conn")
            wait_for_conn = threading.Thread(target=self.wait_for_conn)
            wait_for_conn.start()
        else:
            print(f"Client is trying to connect to {self.connect_addr, self.port}")
            while True:
                try:
                    self.socket.settimeout(20)
                    self.socket.connect((self.connect_addr, self.port))
                except ConnectionRefusedError:
                    print("Connection refused. Trying again in 500 ms")
                    time.sleep(0.5)
                    continue
                except KeyboardInterrupt:
                    exit(0)
                except TimeoutError:
                    print("Connection timeout. Trying again")
                    self.new_conn()
                    return
                    
                else: # only do this if we do not get an error
                    self.waiting_for_conn = False
                    break
            self.conn = self.socket
            print(f"connection from client has been established. conn: {self.conn}")
            # print(self.socket.gettimeout())
            self.socket.settimeout(0.4)

    def wait_for_conn(self) -> None:
        while True:
            print("Server is waiting on connection")
            temp_conn, addr = self.socket.accept()
            self.conn = temp_conn
            self.waiting_for_conn = False
            break
        print(f"New connection from {addr}. conn: {self.conn}, addr")

    def send(self, bytes_to_send: bytes) -> None:
        if self.conn is None and not self.waiting_for_conn:
            raise Exception("Client tried sending with a non existing connection")
        # print(f"waiting for conn: {self.waiting_for_conn}")
        wait_counter = 0
        while self.waiting_for_conn:
            print("waiting for conn"+(wait_counter*"."), end="                 \r")
            wait_counter += 1
            if wait_counter > 5:
                wait_counter = 0
            time.sleep(0.3)
        try:
            if type(bytes_to_send) != bytes:
                print(f"tried sending something that was not bytes: {bytes_to_send = } type: {type(bytes_to_send)}")
                exit(1)
            self.conn.sendall(bytes_to_send)
        except (socket.error, BrokenPipeError)  as e:
            print(f"Tried sending, but got an error \n{e}")
            print(f"conn = {self.conn}, waiting for conn: {self.waiting_for_conn}")
            if not self.waiting_for_conn:
                self.new_conn()

    def receive(self) -> bytes:
        # print(self.conn)
        if self.conn is None:
            if not self.waiting_for_conn:
                print("conn is none and we are not waiting for conn.")
                self.wait_for_conn()
        try:
            if self.conn is not None:
                data = self.conn.recv(999999)
                if data != None:
                    return data
                # else:
                #     return self.receive()
        except socket.error as e:
            print(f"Exception: {e}")

    def exit(self):
        if self.conn is None:
            exit(0)
        self.conn.close()
        self.running = False

# Do not get error here if
def send_forever(conn: socket.socket):
    print("sending forever")
    data = {"test": 2, "abc": [1,2,34]}
    data = bytes(json.dumps(data), "utf-8")
    while True:
        conn.send(data)

def recieve_forever(conn):
    while True:
        data = conn.receive()
        if data is not None:
                if data is not "heartbeat":
                    data:str = bytes.decode(data, "utf-8")
                    temp = b''
                    check = False
                    if check:
                        temp += message
                    elif data[-1] == b"*" and data[0] == b"*":
                        for message in data.split( json.dumps("*") ):
                            try:
                                json.loads(message)
                            except Exception as e:
                                print(message)

                    for message in data.split( json.dumps("*") ):
                        if message is not '' and message is not "heartbeat":
                            if check:
                                check = False
                                temp += message
                            else:
                                if message[-1] == b"*":
                                    pass
                                else:
                                    check = True
                                    temp = message


if __name__ == "__main__":
    print(sys.platform)
    if sys.platform != "win32":
        server_conn = Network(is_server=False, bind_addr="0.0.0.0")
        # server_conn = Network(is_server=True, bind_addr="127.0.0.1")
        # threading.Thread(target=recieve_forever).start()
        while True:
            data = server_conn.receive()
            if not data:
                continue
            print(data)
    else:
        # a = subprocess.call("ssh rov python3 ~/socket_testing/network_handler.py")
        # a = subprocess.Popen("ssh rov touch test")
        # print(os.system("ssh rov touch test")) # python3 ~/socket_testing/network_handler.py"))
        # exit()
        client_conn = Network(is_server=False, bind_addr="0.0.0.0", connect_addr="10.0.0.2")
        nw = threading.Thread(name="Recv_test_tread",target=recieve_forever, daemon=True, args=([client_conn]))
        nw.start()
        while True:
            time.sleep(2)
            asd = [[296, "bildebehandlingsmodus", 1],[500, "teststring"]]
            a = input("Click to send message\n")
            if a == "stop":
                a = input("What cam do you want to stop?\n")
                if a == "front":
                    asd = [[201, {"on": True}]]
                else:
                    asd = [[200, {"on": True}]]
            elif a == "modus":
                a = input("What cam do you want to change mode on?\n")
                if a == "back":
                    a = input("Set mode to what?\n")
                    asd = [[201, {"bildebehandlingsmodus": int(a)}]]
                else:
                    a = input("Set mode to what?\n")
                    asd = [[200, {"bildebehandlingsmodus": int(a)}]]
            elif a == 'tilt':
                a = input("Tilt camera to what angle?\n")
                asd = [[200, {"tilt": int(a)}]]
            elif a == 'loop':
                for _ in range(10):
                    asd = [70]
            elif a == 'pic':
                asd = [[200, {"take_pic": int(7)}]]
            elif a == 'id':
                a = input("ID\n")
                asd = [[int(a), []]]
            elif 'stich':
                print('stitch')
                asd = [[200, {"stitch": int(7)}]]
                
            mess = bytes(json.dumps("*"), "utf-8") + bytes(json.dumps(asd), "utf-8") + bytes(json.dumps("*"), "utf-8")
            client_conn.send(mess)
            #client_conn.send(bytes('*{"can": [(0, 99)]}*', "utf-8"))
        # send_thread = threading.Thread(target=lambda: send_forever(client_conn))
        # send_thread.start()
        # send_thread.join()
        # while True:
        #     time.sleep(1)
    
