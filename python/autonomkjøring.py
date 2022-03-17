from regulator import PID
import cv2
import vision_pipline as vp
import logging




#Filen vision_pipline.py inneholder openCV algoritmer som brukes i denne og andre filer/klasser

class Autonom:
    
    def __init__(self, logger: logging.Logger=None) -> None:
        self.logger = logger.getChild("Autonom")
        self.logger.setLevel(1)
    
    def dock(self) -> None:
        self.logger.info("Autonom docking startet")
        
        
    def merd(self) -> None:
        self.logger.info("Autonom merd skanning startet")
    
    def mosaic(self) -> None:
        self.logger.info("Autonom mosaic startet")
    
    
    
if __name__ == "__main__":
    from logging_init import generate_logging
    
    
    auto_test = Autonom(logger=generate_logging())
    
    
    auto_test.dock()
    









