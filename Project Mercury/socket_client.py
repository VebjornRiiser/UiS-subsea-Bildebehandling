import socket, time

host = "10.0.0.1"
port = 6900

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((host, port))
    print("Enter what you would like to send to the echo server")
    while True:
        data_to_send = input("SKRIV NOE")
        data_to_send = bytes(data_to_send, "utf-8")
        s.sendall(data_to_send)
        data = s.recv(1024)
        print("recieved " + repr(data))