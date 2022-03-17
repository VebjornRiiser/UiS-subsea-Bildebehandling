#Denne filen inneholder funksjoner og klasser for autonom kjøring
import time


class PID:
    def __init__(self,param_dict) -> None:
            self.params = param_dict
            self.proportional = 0
            self.integrator = 0
            self.derivator = 0
            self.prevtime = 0
            
    @property
    def params(self) -> dict:
        return self._params
    
    @params.setter
    def params(self, param_dict:dict) -> None:
        self._params = param_dict
        try:
            self.KP = param_dict["KP"]
            self.KI = param_dict["KI"]
            self.KD = param_dict["KD"]
            self.mode = param_dict["mode"]
            self.nummode = param_dict["nummode"]
            self.ON_OFF_param = param_dict["ON/OFF"]
            self.derivator_klamp = param_dict["derivator_klamp"]
            self.integrator_klamp = param_dict["integrator_klamp"]
            
        except KeyError as e:
            print(f'KeyError: det ser ut som om ikke alle parameteren er satt, dette kan medføre udefinert oppførsel')
            #TODO Konverter til logging -- Dette må vel være på en program level

    @property    
    def mode(self) -> str:
        return self._mode

    @mode.setter
    def mode(self, new_mode:str) -> None:
        self._mode = new_mode
        self._params["mode"] = self._mode

    def calculate_new(self,PV:int|float,SV:int|float) -> int|float:
        self.PV = PV
        self.SV = SV
        self.error = SV - PV
        if self.prevtime == 0:
            samplingtime = 1/20
        else:
            time_now = time.time()
            self.samplingtime = time_now - self.prevtime
            self.prevtime = time_now       

        match self.mode:
            case "P":
                return self.calcP()
            case "I":
                return self.calcI()
            case "D":
                return self.calcD
            case "PI":
                return self.calcP() + self.calcI()
            case "PD":
                return self.calcP() + self.calcD()
            case "PID":
                return self.calcP() + self.calcI() + self.calcD()
            case "ON/OFF":
                pass
        
        self.prevError = self.error
        self.prevPV = self.PV
        
    def calcP(self) -> int|float:
        return self.KP * self.error
    
    def calcI(self) -> int|float:
        self.integrator = self.integrator * 0.5 * self.KI * self.samplingtime * (self.error + self.prevError)
        #TODO Klamping
        
    def calcD(self) -> int|float:
        #derivat on measurement
        self.derivator = -(2 * self.KD *(self.PV - self.prevPV) + (2 * self.tau - self.samplingtime) * self.derivator) / (2*self.tau + self.samplingtime)
        #TODO Klamping
    
    def ON_OFF(self):
        pass
                
    
        
    