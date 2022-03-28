
import cv2
from sys import platform
import numpy as np
import math
from ROV import Rov


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
def vp_dock(bilder, rov_config: Rov=None, stereosyn: bool=True , return_pic: bool=True):
    """_summary_

    Args:
        bilder (list): et eller to bilder som brukes til å docke
        stereosyn (bool, optional): Sier om det er brukt stereosyn eller ikke, blir nok fjernet etterhvert da den ikke er helt opp til standarden vår/min. Defaults to True.

    Returns:
        Any: Info som brukes til å navigere til/inn i docken
        
    """
    #Fysiske konstanter
    #TODO Oppdatert til rele tall'
    if not rov_config:
        rov_height = 100
        rov_width = 100
        rov_depth = 100
        x_area = rov_height*rov_width
        y_area = rov_depth*rov_height
        z_area = rov_depth*rov_width
    else:
        print(f"Bruker ikke ROV konfig per nå") #TODO Implementere dette som en return i forbindelse med logging
        return False
    
    

    #Letter etter en firkant (dock) som roven passer inn i
    
    
    #Algoritme for å docke autonomt

    #Finn sirkel knapp og posisjoner i forhold til den
    gray = cv2.cvtColor(bilder,cv2.COLOR_RGB2GRAY)
    gray = cv2.GaussianBlur(gray,(5,5),0)
    gray = cv2.medianBlur(gray,5)
    gray = cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11,3.5)
    
    #kernel = np.ones((3,3),np.uint8)
    #gray = cv2.erode(gray,kernel,iterations = 1)
    
    #gray = cv2.dilate(gray,kernel,iterations=1)
    
    sirkler = cv2.HoughCircles(gray,cv2.HOUGH_GRADIENT,1,260,param1=30,param2=65,minRadius=0,maxRadius=0)
    
    if sirkler is not None:
        sirkler = np.round(sirkler[0,:]).astype("int")
        for x,y,r in sirkler:
            cv2.circle(output, (x,y), r, (0,255,0),4)
            cv2.rectangle(output, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
    #Finn avstand og størrelse
    
    
    #Returner Posisjon, avstand og rotasjon(skew?)
    
    return output 
        
 
    



def vp_merd(bilde ,stereosyn: bool=True):
    #Algoritme for å inspisere merd, 
    
    # Lete etter hull og gi de en ID
    # holes = {"ID": cv2.rect data type} eller som en liste i samme format
    # navigation = {"direction": int, "v_cor": int|float, "h_cor": int|float, "angle_cor": int|float} eller som en liste i samme format
    holes = {}
    navigation = {}
    threshold_area = 75 # cm
    threshold_error_toleranse = 0.1 #prosent
    
    
    # Finn hull og sorter ut på areal
    if stereosyn:
        pass
    else:
        gray = cv2.cvtColor(bilde,cv2.COLOR_RGB2GRAY)
        gray = cv2.GaussianBlur(gray,(5,5),0)
        gray = cv2.medianBlur(gray,5)
        gray = cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11,3.5)
        
        contours, hierarchy = cv2.findContours(gray,cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        contour_area = np.array([cv2.contourArea(i) for i in contours])
        contour_area = contour_area[(contour_area >= threshold_area)]

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

##----------------------------------Hjelpe funksjoner-----------------------------------##
def angle_vector(pt1: tuple, pt2: tuple, pt0: tuple):
    """Regner ut cosinus mellom to vektorer med samme utgangspunkt
    source: https://docs.opencv.org/3.4/db/d00/samples_2cpp_2squares_8cpp-example.html

    Args:
        pt1 (cv2.Point): vektor 1
        pt2 (cv2.Point): vektor 2
        pt0 (cv2.Point): Origo 

    Returns:
        float: Consinus mellom to vinkelr
    """
    dx1 = pt1[0] - pt0[0]
    dy1 = pt1[1] - pt0[1]
    dx2 = pt2[0] - pt0[0]
    dy2 = pt2[1] - pt0[1]
    return (dx1*dx2+dy1*dy2)/math.sqrt((dx1**2+dy1**2)*(dx2**2 + dy2**2) + 1e-10)


if __name__ == "__main__":
    mode = "dock"
    match mode:
        case "merd":
            filename = f".\\video_test_merd.mp4" #WARNING Windows spesifikt??
        case "dock":
            filename = 0        
    #filename = ".\\merdtesting_1.png"
    cap = cv2.VideoCapture(0)
    
    
    
    while cap.isOpened():
        ret, frame = cap.read()
        if frame is not None:
            #ut_bilde = vp_merd(frame,False)
            ut_bilde = vp_dock(frame)
            cv2.imshow("regulering",ut_bilde[0])
            if cv2.waitKey(25) & 0xFF == ord('q'):
                break
        else:
            break
    cap.release()
    cv2.destroyAllWindows()
