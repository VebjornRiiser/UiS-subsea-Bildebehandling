from json.tool import main
from unicodedata import name
import cv2
import multiprocessing



def camera(camera_id):
    feed = cv2.VideoCapture(camera_id)
    if not (feed.isOpened()):
        print("Could not open video device")
    while True:
        ref, frame = feed.read()
        cv2.imshow(f'Camera:{camera_id}', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        feed.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    camera(1)
