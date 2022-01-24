import socket
import time
import json
from math import mean, max

def venus(ip, port, meld):
    network_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    network_socket.settimeout(10)
    time_list = []
    try:
        network_socket.connect((ip, port))
    except Exception as e:
        print(e)
        print("Could not connect to network")
        exit()
    for __ in range(50):
        time.sleep(2)
        try:
            start = time.time_ns()
            network_socket.sendall(str.encode(meld))
            recmeld = network_socket.recv(1024)
            print(time_list.append(time.time_ns()))
        except Exception as e:
            print(e)
            print("Connection lost")
            break
    time.sleep(1)
    network_socket.close()
    print(f'Mean time per package:{mean(time_list)}\nMax time for one package:{max(time_list)}')
    return "ok"

if __name__ == "__main__":
    print("Main=client")
    dictionary = {"can":[(59,"datadata"), (59,"epleeple"), (59, "datadata")]}
    meld = json.dumps(dictionary)
    ip = "10.0.0.2"
    port = 6900
    svar = print(venus(ip, port, meld))
    