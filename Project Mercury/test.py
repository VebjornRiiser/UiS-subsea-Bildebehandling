# enkel server applikasjon
import pickle as p
import socket

def send_command(command,svar,conn,byte=1024):
    msg = p.dumps(command)
    while True:
        conn.sendall(msg)
        byte_inn = conn.recv(byte)
        data = p.loads(byte_inn)
        if data == svar:
            return command, svar



# setup
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(("192.168.0.111",50000))
msg = 0


while True:
        print(f"Awaiting conneting....")
        s.listen(1)
        conn, addr = s.accept()
        print(f"Koblet til med med addresse: {addr[0]}, port: {addr[1]}")

        while 1:
            kommando,svar =  send_command("klar","ja",conn)
            print(f"{kommando} sent og motatt med svaret: {svar}")