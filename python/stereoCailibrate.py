
import os
import cv2
import numpy as np
import glob
import argparse
import time
import winsound


parser = argparse.ArgumentParser()
parser.add_argument('--MODE',)
parser.add_argument('-cid','--CAMID', type=int)
parser.add_argument('-gs','--GRAB_SPLIT', action="store_true" )
parser.add_argument('-g','--GRAB',action="store_true")
parser.add_argument('-r','--ROWS',default=6, type=int)
parser.add_argument('-col','--COLUMNS',default=7, type=int)
parser.add_argument('-num','--NUMBER', default=10, type=int)

def grab_split_frames_from_folder(camid):
    image_folder = f".\\Calibrate_camera_{camid}\\*"
    bilde_navn = sorted(glob.glob(image_folder))
    bilder_l = []
    bilder_r = []
    split_line = int(2560/2) #TODO denne burde ikke hvert slik, heller dynamisk
    for i in bilde_navn:
        bilde = cv2.imread(i, 1)
        bilde_l, bilde_r = bilde[:,:split_line], bilde[:,split_line:]
        bilder_l.append(bilde_l)
        bilder_r.append(bilde_r)
    return bilder_l,bilder_r
    
def contrast_boost(img):
    lab= cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    #-----Splitting the LAB image to different channels-------------------------
    l, a, b = cv2.split(lab)

    #-----Applying CLAHE to L-channel-------------------------------------------
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    cl = clahe.apply(l)

    #-----Merge the CLAHE enhanced L-channel with the a and b channel-----------
    limg = cv2.merge((cl,a,b))
    

    #-----Converting image from LAB Color model to RGB model--------------------
    final = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
    
    return final


argumenter = parser.parse_args()



if argumenter.MODE.lower() in ('cal'):
    if argumenter.GRAB_SPLIT:
        left_pic,right_pic = grab_split_frames_from_folder(argumenter.CAMID)
        kriterium = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 35, 0.001)
        
        rows = argumenter.ROWS
        columns = argumenter.COLUMNS
        world_scaling = 1 
        objp = np.zeros((rows*columns,3),np.float32)
        objp[:,:2] = np.mgrid[0:rows,0:columns].T.reshape(-1,2)
        objp = world_scaling * objp
        
        
        width = left_pic[0].shape[1]
        height = left_pic[0].shape[0]
        
        impoints = []
        objpoints = []
        
        for side in [left_pic,right_pic]:
            
            for bilde in side:
                gray = cv2.cvtColor(bilde, cv2.COLOR_BGR2GRAY)
                #gray = cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11,3.5)
                #ret, gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
                ret, corners = cv2.findChessboardCorners(gray, (rows, columns), None)
                cv2.imshow("img", gray)
                k = cv2.waitKey(500)
                if ret == True:
                    conv_size = (11,11)
                    
                    corners = cv2.cornerSubPix(gray, corners, conv_size, (-1,-1), kriterium)
                    cv2.drawChessboardCorners(bilde, (rows,columns), corners, ret)
                    cv2.imshow("img", bilde)
                    k = cv2.waitKey(500)
                    
                    objpoints.append(objp)  
                    impoints.append(corners)      
                else:
                    print("Fant ingen ruter")
                    
            ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, impoints, (width, height), None, None) #mtx og dist som er interessante
            print('rmse:', ret)
            print('camera matrix:\n', mtx)
            print('distortion coeffs:', dist)
            print('Rs:\n', rvecs)
            print('Ts:\n', tvecs)
        
elif argumenter.MODE == 'pic':
    os.system('mkdir Calibrate_camera_1')
    os.system('mkdir Calibrate_camera_2')
    vid = cv2.VideoCapture(0)
    vid.set(cv2.CAP_PROP_FRAME_HEIGHT, 960)
    vid.set(cv2.CAP_PROP_FRAME_WIDTH, 2560)
    bildenummer = 0
    total_tid = 5
    while bildenummer < argumenter.NUMBER:
        winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)
        for tid in range(total_tid):
            time.sleep(1)
            print(f'Ventet i {tid+1} av {total_tid}')
            
            
        ret, frame = vid.read()
        cv2.imwrite(f'.\\Calibrate_camera_{argumenter.CAMID}\\{bildenummer}_cal_bilde.png', frame)
        bildenummer += 1
        
    cv2.destroyAllWindows() 
    vid.release()




