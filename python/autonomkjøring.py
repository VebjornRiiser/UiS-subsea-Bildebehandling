
from regulator import PID
import cv2
import vision_pipline as vp





#Filen vision_pipline.py inneholder openCV algoritmer som brukes i denne og andre filer/klasser

class Autonom:
    def __init__(self) -> None:
        pass
    
    def dock(self) -> None:
        pass
    
    def merd(self) -> None:
        pass
    
    def mosaic(self) -> None:
        self.logger.info("Autonom mosaic startet")
        # STARTUP kode for mosaic -- En form for kalibrering og info til operatør om hva som skjer og en bekreftelse av noe slag
        
        # Henter bilde -- gir bilde en ID og en plass i rutenettet som det skal plasseres i
        # VP kode for navigasjon -- Navigere seg etter etter rutenettet
        vp_mosaic_feedback = vp.vp_mosaic()
        if isinstance(vp_mosaic_feedback, str):
            self.logger.error(vp_mosaic_feedback)
        else:
            #kode for å gjøre no med VP data
            pass
        
        
        # HENT regulator verdier med data fra VP kode
        # SEND kjøredata til CAN (hermes)
        # SEND bilde og evt data opp til topside
        
        # VP kode for mosaic -- utfører sammenslåing av bilde som er blitt tatt, med utgangspunkt i ID og rutenett posisjon


        
if __name__ == "__main__":
    from logging_init import generate_logging
    
    
    auto_test = Autonom(logger=generate_logging())
    
    
    auto_test.dock()
    









