from inspect import currentframe, getframeinfo
import subprocess

# Print info om nåværende linje.
def ln(melding:str=""):
    cf = currentframe()
    print(f"Linjenummer: {cf.f_back.f_lineno}, {melding + ', ' if melding != '' else ''}fil: { getframeinfo(cf.f_back).filename.split('/')[-1] }")

def get_apu_temp(string_out=True):
    temperature = subprocess.check_output("sensors | grep \"Tdie\" | tr -s ' ' " " | cut -d ' ' -f 2", shell=True)[:-1].decode('utf-8')
    if string_out:
        return temperature
    else:
        return float(temperature.replace('°C', ''))