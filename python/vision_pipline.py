
import cv2
from sys import platform
import numpy as np
import math
from ROV import Rov
from logging_init import generate_logging
import timeit


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
def vp_dock_st(bilder, rov_config: Rov=None , return_pic: bool=True, logger = None):
    """_summary_

    Args:
        bilder (list): et eller to bilder som brukes til å docke
        stereosyn (bool, optional): Sier om det er brukt stereosyn eller ikke, blir nok fjernet etterhvert da den ikke er helt opp til standarden vår/min. Defaults to True.

    Returns:
        Any: Info som brukes til å navigere til/inn i docken
        
    """
    if not logger: #WARNING Kan medføre performance loss hvis kalt opp hver gang funksjonene må kjøre
        logger = generate_logging(log_name="vp_dock",log_file_name="vp_dock.log")
    
    #Fysiske konstanter
    #TODO Oppdatert til rele tall'
    if not rov_config:
        rov_height = 100
        rov_width = 100
        rov_depth = 100
        x_area = rov_height*rov_width
        y_area = rov_depth*rov_height
        z_area = rov_depth*rov_width
        #logger.info("Fysisk ROv størrelse oppdatert og i bruk")
    else:
        return False
    ##-----inital variabler----------##
    squares = []
    max_cos = 0
    kernel = np.ones((3,3),np.uint8)
   
    
    #TODO --> Støy og preprosses portes til en egen funkson og brukes sammen med denne 
    filtrerte_bilder = [cv2.GaussianBlur(bilde, (5,5), 0) for bilde in bilder] # støyredusering som tar vare på kanter
    gray_bilder = [cv2.cvtColor(bilde, cv2.COLOR_BGR2GRAY) for bilde in bilder] # Gjør om til grått
    #---------------------------------------------------------------------------
    
    threshold_bilder = [cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11,2) for gray in gray_bilder]
    
    
    
    contours_l, hirarchy = cv2.findContours(threshold_bilder[0], cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    if not contours_l:
        logger.warning("Fant ingen conturer i venstre bilde, antar at det ikke finnes noe i høyre.")
        return None
    
    
    
    
    contours_r, hirarchy = cv2.findContours(threshold_bilder[1], cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    if len(contours_l) != len(contours_r): #TODO mulig det blir feil å ikke sortere disse listene før man gjør dette
        #prioriterer contrours_l
        logger.info("Fant ulik mengde konturer i venstre og høyre bilde, bruker antall konturer funnet i venstre bilde")
        contours_r = contours_r[:len(contours_l)]
    
    
    
    
    
    for L_cnt, r_cnt in zip(contours_l, contours_r):
        cnt_len = cv2.arcLength(cnt, True)
        cnt = cv2.approxPolyDP(cnt, 0.02*cnt_len, True)
        area = cv2.contourArea(cnt)
        if len(cnt) == 4 and cv2.contourArea(cnt) > 1000 and cv2.isContourConvex(cnt): #TODO port fra pixler til cm
            for j in range(2,5):
                #msg = f"{j=} --> {cnt[j%4][0]=},{cnt[j-2][0]=},{cnt[j-1][0]=}"
                #logger.debug(msg)
                max_cos = max(max_cos, angle_vector(cnt[j%4][0], cnt[j-2][0],cnt[j-1][0]))
            if max_cos < 0.3:
                squares.append(cnt)
                logger.info(f"Found square with area: --> {area} pixel^2")
                # Her har vi funnet en stor firkant så da kan vi lete etter sirkler i det hirarikitet ??
    return squares

    



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
        
        # Finne størrelsen på hullet i cm^3 slik at man kan skjekk det mot en threshold
        

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
def kontrast_boost(bilde):
    # Konverter bilde til LAB color space
    lab = cv2.cvtColor(bilde, cv2.COLOR_BGR2LAB)
    l,a,b = cv2.split(lab)
    
    clahe = cv2.createCLAHE(clipLimit=3, tileGridSize=(8,8))
    cl = clahe.apply(l)
    
    limg = cv2.merge((cl,a,b))
    final = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
    return final




##--------------------------------------------------------------------------------------##

##----------------------------------Hjelpe funksjoner-----------------------------------##
def angle_vector(pt1: tuple, pt2: tuple, pt0: tuple):
    """Regner ut cosinus mellom to vektorer
        source: https://docs.opencv.org/3.4/db/d00/samples_2cpp_2squares_8cpp-example.html

    Args:
        pt1 (cv2.Point): vektor 1
        pt2 (cv2.Point): vektor 2
        pt0 (cv2.Point): Origo 

    Returns:
        float: Consinus mellom to vinkelr
    """
    pt1 = pt1.astype(np.float32)
    pt2 = pt2.astype(np.float32)
    pt0 = pt0.astype(np.float32)
    dx1 = pt1[0] - pt0[0]
    dy1 = pt1[1] - pt0[1]
    dx2 = pt2[0] - pt0[0]
    dy2 = pt2[1] - pt0[1]
    return (dx1*dx2+dy1*dy2)/math.sqrt((dx1**2+dy1**2)*(dx2**2 + dy2**2) + 1e-10)

def angle_cos(p0, p1, p2): 
    """Regner ut cosinus mellom to vektorer
        Soruce: https://github.com/opencv/opencv/blob/3.2.0/samples/python/squares.py
    Args:
        p0 (_type_): _description_
        p1 (_type_): _description_
        p2 (_type_): _description_

    Returns:
        _type_: _description_
    """
    d1, d2 = (p0-p1).astype('float'), (p2-p1).astype('float')
    return abs( np.dot(d1, d2) / np.sqrt( np.dot(d1, d1)*np.dot(d2, d2) ) )

def calc_distance(centers, focal_len=2098, camera_space=60, int_float: int=0): # Calculates distance to object using test data, needs position on object in two pictures
    """Regner ut distansen til et objekt. for stereo kamera

    Args:
        centers (_type_): Senterkoortdinat til objektet i begge bildene
        focal_len (float, optional): Focallength oppgitt i pixler. Defaults to 33.2.
        camera_space (int, optional): Distansen mellom kameraene i mm. Defaults to 60.
        int_float (int, optional): Bestemmer om funksjonen skal returnere tall i INT->(0) eller FLOAT->(1). Defaults to 0
    Returns:
        int|float: Avstand i mm
    """
    dist = abs(centers[0][0]-centers[1][0])
    print(dist)
    if dist == 0:
        return 50
    #return int((3.631e-6 * (dist**4)) - (0.003035 * (dist**3)) + (0.9672 * (dist**2)) - (139.9 * dist) + 7862)
    if int_float:
        return float(((focal_len*camera_space)/dist))
    else:
        return int(((focal_len*camera_space)/dist)) #TODO trenger det å være INT her??


if __name__ == "__main__":
    main_logger = generate_logging(log_name="VP_main_test",log_file_name="VP_main.log")
    vid = cv2.VideoCapture(0)
    vid.set(cv2.CAP_PROP_FRAME_HEIGHT, 960)
    vid.set(cv2.CAP_PROP_FRAME_WIDTH, 2560)
    main_logger.info(f"Kamera HW-ACC satt til: --> {vid.get(cv2.CAP_PROP_HW_ACCELERATION)}")
    main_logger.info(f"Bilde høyde er satt til: --> {vid.get(cv2.CAP_PROP_FRAME_HEIGHT)}")
    main_logger.info(f"Bilde bredde er satt til: --> {vid.get(cv2.CAP_PROP_FRAME_WIDTH)}")
    
    
    
    
    while True:
        ret, frame = vid.read()
        split_line = int(2560/2)
        frame = frame[:,:split_line], frame[:,split_line:]
     
        
        
        squares = vp_dock_st(frame,logger=main_logger)
        #cv2.drawContours(frame, squares, -1, (0,255,0), 3, cv2.LINE_AA)
        for name, i in zip(["Left","Right"],frame):
            cv2.imshow(name, i)
        if cv2.waitKey(3) == 27:
            break
    cv2.destroyAllWindows() 
    cv2.VideoCapture(0).release()