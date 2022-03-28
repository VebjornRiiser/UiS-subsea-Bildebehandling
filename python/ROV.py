class Rov:
    def __init__(self) -> None:
        self.height = 100
        self.width = 100
        self.length = 100
        self.area = Rov.area(self.height, self.length, self.width)
        
    def check_fit(self,area_to_check: int|float, rov_plane: str):
        return area_to_check >= self.area[rov_plane.lower()]
    
    
    
    @staticmethod
    def area(heigh,lenght,width) -> tuple:
        area = {}
        area["x"] = heigh*width
        area["y"] = lenght*heigh
        area["z"] = lenght*width
        
        return area