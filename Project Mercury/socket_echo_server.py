import socket

host = "0.0.0.0"

port = 6900

with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s: # SOCK_STREAM means tcp
    s.bind((host,port))
    s.listen()
    conn, addr = s.accept()
    with conn:
        print("connected to " + str(addr))
        while True:
            data = conn.recv(1024)
            if not data:
                break
            print("recieved " + repr(data))
            conn.sendall(data)