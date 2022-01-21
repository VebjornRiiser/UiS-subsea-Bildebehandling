from email.policy import default
from platform import platform
import cv2
import numpy as np
import click
from sys import platform


@click.command()
@click.option('--cam_id',default=2,help='Hvilket kamera som skal åpnes')
@click.option('--fps',default=30,help='Bildefrekvensen til kameraet')
@click.option('--hw',default=1,help='Aktiverer maskinvareakselerasjon')
def main(cam_id,fps,hw):
    #Bruk av hardware decoding
    HW = hw
    HW_device = 1 #0 = iGPU ++
    HW_type = 1 # 0 = none, 1 = any, 2 = D311, 3 = VAAPI, 4 = MFX

    CAM_ID = cam_id
    FPS = fps
    HØYDE = 2560
    BREDDE = 960

    if platform in ("linux","linux2"):
        print('Åpner kameraet på linux --> V4L2 driver')
        camera = cv2.VideoCapture(CAM_ID,cv2.CAP_V4L2)
    else:
        print('Åpner kameraet på windows')
        camera = cv2.VideoCapture(CAM_ID)
    if not camera.isOpened():
        print("Kunne ikke åpne kameraet")
        exit()
    
    print('Endrer på instillinger')    
    stat1 = camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M','J','P','G'))
    stat2 = camera.set(cv2.CAP_PROP_FRAME_WIDTH,HØYDE)
    stat3 = camera.set(cv2.CAP_PROP_FRAME_HEIGHT,BREDDE)
    stat4 = camera.set(cv2.CAP_PROP_FPS, FPS)

    if HW:
       stat5 = camera.set(cv2.CAP_PROP_HW_ACCELERATION, HW_type)
       stat6 =  camera.set(cv2.CAP_PROP_HW_DEVICE,HW_device)

    status_liste = [stat1,stat2,stat3,stat4,stat5,stat6]
        
    status_msg = f'-----------------Status------------------\n'
    status_msg = f'Høyde --> {camera.get(cv2.CAP_PROP_FRAME_HEIGHT)}\n'\
                f'Bredde --> {camera.get(cv2.CAP_PROP_FRAME_WIDTH)}\n'\
                f'FPS --> {camera.get(cv2.CAP_PROP_FPS)}\n'\
                f'Hardware akselerasjon --> {camera.get(cv2.CAP_PROP_HW_ACCELERATION)}\n'\
                f'Bitrate --> {camera.get(cv2.CAP_PROP_BITRATE)}\n'\
                f'{status_liste.count(True)} av {len(status_liste)} instillinger ble satt'

    print(status_msg)
   
       
            

    while True:
        ret, frame = camera.read()
        #frame = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        cv2.imshow("Stereo kamera", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
    camera.release()

    cv2.destroyAllWindows()
    
main()