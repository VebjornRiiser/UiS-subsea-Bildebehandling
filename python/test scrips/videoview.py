import cv2

class Cascade_finder():
    def __init__(self, xmlpath):
        self.fish_cascade = cv2.CascadeClassifier(xmlpath)
        # Possible to add more cascades...


    def find_fish(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)
        fish = self.fish_cascade(gray)
        print(fish)
        #for (x,y,w,h) in fish:
        #    cv2.rectangle(image, (x,y), (w,h), (255,0,0), 2)


def videoviewer(videopath, xmlpath):
    feed = cv2.VideoCapture(xmlpath)
    a = Cascade_finder()
    if not feed.isOpened():
        print(f'Could not open video')
        return
    while feed.isOpened():
        bol , image = feed.read()
        if bol:
            a.find_fish(image)
            cv2.imshow('VideoStream', image)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break


if __name__ == "__main__":
    videoviewer(path1, path2)

