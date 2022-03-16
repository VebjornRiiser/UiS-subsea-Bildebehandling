from ctypes import sizeof
import socket
import numpy
import time
import cv2
import pickle as p

UDP_IP="10.0.0.1"
UDP_PORT = 6888
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

pic=b''
empty_frame = numpy
max = 0
frames = 0
start = time.time()
print("TEST")
pack_len = 30000
new_pack_len = 30000
counter = 6
while True:
    pic = b''
    data, addr = sock.recvfrom(62000)
    try:
        liste = p.loads(data)
    except Exception:
        liste = [0]

    if liste[0] == 'start':
        new_pack_len = liste[1]
        counter = liste[2]
        for __ in range(counter):
            data, addr = sock.recvfrom(62000)
            pic += data
        if len(pic) >= 5000:
        #pic = (1,pic)
            frame = numpy.frombuffer(pic, dtype=numpy.uint8)
        #if len(frame) == 921600: # Old package size 3686400
            #frame = frame.reshape(480,640,3)
            frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
            try:
                cv2.imshow("frame",frame)
            except Exception as e:
                print(e)
            frames += 1
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print(frames)
                print(time.time()-start)
                break

