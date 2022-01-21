from ctypes import sizeof
import socket
import numpy
import time
import cv2
import pickle as p

UDP_IP="10.0.0.1"
UDP_PORT = 6889
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
    data, addr = sock.recvfrom(60000)

    for __ in range(counter):
        data, addr = sock.recvfrom(60000)
        
        try:
            liste = p.loads(data)
            if liste[0] == 'start':
                new_pack_len = data[1]
                counter = data[2]
                break
        except:
            pass

        pic += data
    if len(pic) >= pack_len:
        pack_len = new_pack_len
    #pic = (1,pic)
        frame = numpy.frombuffer(pic, dtype=numpy.uint8)
    #if len(frame) == 921600: # Old package size 3686400
        #frame = frame.reshape(480,640,3)
        frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
        cv2.imshow("frame",frame)
        frames += 1
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print(frames)
            print(time.time()-start)
            break