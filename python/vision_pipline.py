import cv2
from sys import platform
import numpy as np

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
def vp_dock():
    #Algoritme for å docke autonomt
    pass


def vp_merd():
    #Algoritme for å inspisere merd, 
    pass

def vp_distance():
    #Algoritme for å regne ut avstand og størrelse
    pass


def vp_mosaic():
    #Algoritme for å lage en mosaikk
    pass


def vp_operator_tools():
    #Algoritme for styring av opperatør verktøy
    pass

##----------------------------------Bilde operasjoner-----------------------------------##




##--------------------------------------------------------------------------------------##


if __name__ == "__main__":
    pass