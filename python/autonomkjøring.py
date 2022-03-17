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
        self.logger.info("Autonom docking startert")
        self.logger.debug("Debug melding")
        self.logger.warning("Muligens ikke noe kode her")
        self.logger.error("Program fungerte ikke")
        self.logger.critical("Kritisk logikk feil")
        
        
    def merd(self) -> None:
        pass
    
    def mosaic(self) -> None:
        pass
    
    
    
if __name__ == "__main__":
    from logging_init import generate_logging
    
    
    auto_test = Autonom(logger=generate_logging())
    
    
    auto_test.dock()
    









