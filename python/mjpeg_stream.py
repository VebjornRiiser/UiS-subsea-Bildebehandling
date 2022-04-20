#!/usr/bin/python
'''
	Author: Igor Maculan - n3wtron@gmail.com
	A Simple mjpg stream http server
'''
from doctest import ELLIPSIS_MARKER
from multiprocessing import Pipe
import multiprocessing
import cv2
from http.server import BaseHTTPRequestHandler,HTTPServer
from io import StringIO
import time
capture=None

class CamHandler(BaseHTTPRequestHandler):
    #def __init__(self, requests, client_address, server):
    #    BaseHTTPRequestHandler.__init__(self, requests, client_address, server)
    #    self.blank = cv2.imencode(".jpg", cv2.imread("blank.jpg"))

    def do_GET(self):
        if self.path.endswith('.mjpg'):
            self.send_response(200)
            self.send_header('Content-type','multipart/x-mixed-replace; boundary=frame')
            self.end_headers()
            while True:
                try:
                    # rc, img = capture.read()
                    if self.server.pipe.poll(0.2):
                        img = self.server.pipe.recv()
                        if isinstance(img, str):
                            print("got string")
                            if img.lower() == "stop": # Closes prosess
                                print("stopping video stream")
                                self.server.socket.close()
                                if self.video_cap:
                                    self.video.release()
                                break
                        else:
                            # if not rc:
                            #     continue
                            # imgRGB=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
                            _, jpg = cv2.imencode(".jpg", img)
                            self.wfile.write(b"--frame\n")
                            self.send_header('Content-type','image/jpeg')
                            self.send_header('Content-length',str(len(jpg)))
                            self.end_headers()
                            self.wfile.write(bytes(jpg))
                            #time.sleep(0.016)
                    else:
                        try:
                            self.blank
                        except:
                            self.blank = cv2.imread("blank.jpg")
                            _, self.blankjpg = cv2.imencode(".jpg", self.blank)
                        self.wfile.write(b"--frame\n")
                        self.send_header('Content-type','image/jpeg')
                        self.send_header('Content-length',str(len(self.blankjpg)))
                        self.end_headers()
                        self.wfile.write(bytes(self.blankjpg))
                except KeyboardInterrupt:
                    break
            return
        if self.path.endswith('.html'):
            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()
            self.wfile.write(b'<html><head></head><body>')
            self.wfile.write(b'<img height="100%" src="http://10.0.0.2:' + bytes(str(self.server.port),'utf-8') + b'/cam.mjpg"/>')
            self.wfile.write(b'</body></html>')
            return

def capture_and_send(pipe):
    # print("here")
    while True:
        rc, img = capture.read()
        if not rc:
                continue
        # print("sent img")
        croped_img = img[:720, :1280]
        pipe.send(croped_img)

# takes raw cv2 img, encodes it and creates a web server that will stream mjpeg.
def run_mjpeg_stream(pipe, port):
    try:
        server = HTTPServer(('0.0.0.0', port), CamHandler)
        print("server started")
        server.pipe = pipe
        server.port = port
        server.serve_forever()
    except KeyboardInterrupt:
        capture.release()
        server.socket.close()


def main():
    global capture
    global img
    capture = cv2.VideoCapture(0, cv2.CAP_V4L2)
    capture.set(cv2.CAP_PROP_FPS, 30)
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, 2560)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    send_pipe, recieve_pipe = Pipe()

    stream = multiprocessing.Process(target=run_mjpeg_stream, args=(recieve_pipe, 8080))
    stream.start()
    capture_and_send(send_pipe)
    

if __name__ == '__main__':
	main()
