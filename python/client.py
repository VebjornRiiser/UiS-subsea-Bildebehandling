import socket
import time
import json

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


if __name__ == "__main__":
    print("Main=client")
    dictionary = {"CAN":1, "camera": 1}
    meld = json.dumps(dictionary)
    ip = "10.0.0.2"
    port = 6900
    for __ in range(9999):
        venus(ip, port, meld)
        time.sleep(1)
