#Denne filen inneholder funksjoner og klasser for autonom kjøring
from pickletools import read_uint1
import time
import logging

class PID:
    def __init__(self,param_dict, logger: logging.Logger=None, name: str="default") -> None:
            self.logger = logger.getChild(f"PID_{name}")
            self.logger.setLevel(1)
            self.name = name
            
            self.params = param_dict
            self.proportional = 0
            self.integrator = 0
            self.derivator = 0
            self.prevtime = 0
    @property
    def name(self) -> str:
        return self._name
    @name.setter
    def name(self, new_name) -> None:
        self._name = new_name
    
    
        
    
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
            self.samplingtime = 1/20
        else:
            time_now = time.time()
            self.samplingtime = time_now - self.prevtime
            self.prevtime = time_now       

        self.prevError = self.error
        self.prevPV = self.PV
        
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
        
    def calcP(self) -> int|float:
        return self.KP * self.error
    
    def calcI(self) -> int|float:
        self.integrator = self.integrator * 0.5 * self.KI * self.samplingtime * (self.error + self.prevError)
        if self.integrator_klamp[0] < self.integrator:
            return self.integrator_klamp[0]
        elif self.integrator_klamp[1] > self.integrator:
            return self.integrator_klamp[1]
        else:
            return self.integrator
        
    def calcD(self) -> int|float:
        #derivat on measurement
        self.derivator = -(2 * self.KD *(self.PV - self.prevPV) + (2 * self.tau - self.samplingtime) * self.derivator) / (2*self.tau + self.samplingtime)
        if self.derivator_klamp[0] < self.derivator:
            return self.derivator_klamp[0]
        elif self.derivator_klamp[1] > self.derivator:
            return self.derivator_klamp[1]
        else:
            return self.derivator
        
    def ON_OFF(self):
        pass
                
    
        
    