from ctypes import sizeof
import socket
import numpy
import time
import cv2

UDP_IP="127.0.0.1"
UDP_PORT = 6888
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

pic=b''
empty_frame = numpy
max = 0
frames = 0
start = time.time()
while True:
    #data, addr = sock.recvfrom(61440)
    pic = b''
    for __ in range(6):
        data, addr = sock.recvfrom(61440)
        if data == b'start':
            break
        pic += data
    if len(pic) > 30000:
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