import cv2
from sys import platform
import numpy as np
import math

##------------------------Klasser------------------------------------##
class Object(): #WARNING Denne klassen er endret fra distance.py så dropin kompabilitet er ikke garantert
    def __init__(self, contour  ) -> None:
        self.rectanlge = cv2.minAreaRect(contour)
        self.angle = self.rectanlge[2]
        self.box = [np.int0(cv2.boxPoints(self.rectanlge))] # Added into a list due to easier use in draw contours
        self.position = (int(self.rectanlge[0][0]), int(self.rectanlge[0][1]))
        self.width = int(self.rectanlge[1][0])
        self.height = int(self.rectanlge[1][1])
        self.true_width = 0
        self.areal = self.width*self.height
        self.contour = contour
        self.dept = 0

    @property
    def box(self):
        return self._box
    @box.setter
    def box(self, box):
        self._box = box

    @property
    def rectangle(self):
        return self._rectanlge
    @rectangle.setter
    def rectangle(self, rectangle):
        self._rectanlge = rectangle
        
    @property
    def position(self):
        return self._position
    @position.setter
    def position(self, position):
        self._position = position
    
    @property
    def width(self):
        return self._width
    @width.setter
    def width(self, width):
        self._width = width

    @property
    def height(self):
        return self._height
    @height.setter
    def height(self, height):
        self._height = height
    
    @property
    def areal(self):
        return self._areal
    @areal.setter
    def areal(self,areal):
        self._areal = areal
    
    @property
    def contour(self):
        return self._contour
    @contour.setter
    def contour(self, contour):
        self._contour = contour
        
    @property
    def dept(self):
        return self._dept
    @dept.setter
    def dept(self, dept):
        self._dept = dept
        
    
    @property
    def true_width(self):
        return self._true_width
    @true_width.setter
    def true_width(self,true_width):
        self._true_width = true_width

##--------------------------------------VP kode--------------------------------------##
def vp_dock(bilde, stereosyn: bool=True):
    #Algoritme for å docke autonomt
    if stereosyn:
        #Finn sirkel knapp og posisjoner i forhold til den
        
        
        #Finn avstand og størrelse
        
        
        #Returner Posisjon, avstand og rotasjon(skew?)
        
        
        
        
        pass
    else:
        return "Kode for singel kamera ikke implementert"
    pass


def vp_merd(bilde ,stereosyn: bool=True):
    #Algoritme for å inspisere merd, 
    
    # Lete etter hull og gi de en ID
    # holes = {"ID": cv2.rect data type} eller som en liste i samme format
    # navigation = {"direction": int, "v_cor": int|float, "h_cor": int|float, "angle_cor": int|float} eller som en liste i samme format
    holes = {}
    navigation = {}
    
    # Finn hull og sorter ut på areal
    if stereosyn:
        pass
    else:
        #blur
        output = np.copy(bilde)
        #bilde = cv2.cvtColor(bilde, cv2.COLOR_)
        blur_bilde = cv2.medianBlur(bilde,5)
        ret, thresh = cv2.threshold(blur_bilde, 150,255, cv2.THRESH_BINARY_INV)
        # Color mask av en farge som ser ut som rød
        
        contours, hierarchy = cv2.findContours(thresh,cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        
        for contour in contours:
            M = cv2.moments(contour)
            if M['m00'] != 0:
                cx = int(M['m10']/M['m00'])
                cy = int(M['m01']/M['m00'])
            #Markerer senter av konturene
            cv2.circle(output, (cx, cy), 7, (255, 255, 255), -1)
            print(math.degrees(math.atan2(cy,cx)+math.pi))
        cv2.drawContours(output,contours,-1,(0,255,0),3)
        #return "Kode for singel kamera ikke implementert"
    # Gi data for navigasjonene langs en linje
    
    return output

def vp_distance():
    #Algoritme for å regne ut avstand og størrelse
    pass


def vp_mosaic(stereosyn: bool=True):
    #Algoritme for å lage en mosaikk
    if stereosyn:
        pass
    else:
        return "Kode for singel kamera ikke implementert"

def vp_operator_tools():
    #Algoritme for styring av opperatør verktøy
    pass

##----------------------------------Bilde operasjoner-----------------------------------##




##--------------------------------------------------------------------------------------##


if __name__ == "__main__":
    filename = f".\\video_test_merd.mp4" #WARNING Windows spesifikt??
    cap = cv2.VideoCapture(filename)
    
    
    
    while cap.isOpened():
        ret, frame = cap.read()
        if ret:
            #ut_bilde = vp_merd(ret,False)
            cv2.imshow("regulering",ret)
            if cv2.waitKey(25) & 0xFF == ord('q'):
                break
        else:
            break
    cap.release()
    cv2.destroyAllWindows()
