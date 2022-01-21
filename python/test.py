#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import time
import cv2
rtmp_url = "rtmp://127.0.0.1:1935/live/test"

# In my mac webcamera is 0, also you can set a video file name instead, for example "/home/user/demo.mp4"
path = 1
cap = cv2.VideoCapture(path, cv2.CAP_V4L2)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

# gather video info to ffmpeg
fps = int(cap.get(cv2.CAP_PROP_FPS))
print(fps)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
# command and params for ffmpeg
command = ['ffmpeg',
           '-y',
           #'-vaapi_device', '/dev/dri/renderD128',
           #'-hwaccel', 'vaapi',
           #'-hwaccel_output_format', 'vaapi',
           '-re',
           '-f', 'v4l2', '-input_format', 'yuyv422', '-s', '640x480', '-r', '30', '-i', '/dev/video0',
           #'-f', 'rawvideo',
           #'-vcodec', 'rawvideo',
           #'-pix_fmt', 'bgr24',
           #'-s', "{}x{}".format(width, height),
           #'-r', str(fps),
           #'-i', '-',
           #'-vf', 'format=nv12,hwupload',
           #'-c:v', 'h264_vaapi',
           '-c:v', 'libx264',
           '-g', '50',
           '-max_delay', '0',
           #'-b:v', '5M', '-profile', '578', '-bf', '0',
           '-threads', '0',
           #'-pix_fmt', 'vaapi_vld',
           '-preset', 'ultrafast',
           '-tune', 'zerolatency',
           '-f', 'mpegts',
           'udp://192.168.137.2:5001'
           #rtmp_url
           ]

# using subprocess and pipe to fetch frame data
p = subprocess.Popen(command, stdin=subprocess.PIPE)


while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("frame read failed")
        break

    # YOUR CODE FOR PROCESSING FRAME HERE
    #cv2.imshow("ss", frame)
    #cv2.waitKey(1)
    # write to pipe
    p.stdin.write(frame.tobytes())