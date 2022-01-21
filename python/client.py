import socket
import time
import json

def venus(ip, port, meld):
    network_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    network_socket.settimeout(3)
    try:
        network_socket.connect((ip, port))
    except Exception as e:
        print(e)
        print("Could not connect to network")
        exit()
    for __ in range(50):
        time.sleep(2)
        try:
            network_socket.sendall(str.encode(meld))
        except Exception as e:
            print(e)
            print("Connection lost")
            break
        #recmeld = network_socket.recv(1024)
    time.sleep(1)
    network_socket.close()
    return "ok"

if __name__ == "__main__":
    print("Main=client")
    dictionary = {"can":[(59,"datadata"), (59,"epleeple"), (59, "datadata")]}
    meld = json.dumps(dictionary)
    ip = "10.0.0.2"
    port = 6900
    svar = print(venus(ip, port, meld))
    