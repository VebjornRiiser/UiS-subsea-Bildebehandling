from inspect import currentframe, getframeinfo

# Print info om nåværende linje.
def ln(melding:str=""):
    cf = currentframe()
    print(f"Linjenummer: {cf.f_back.f_lineno}, {melding + ', ' if melding != '' else ''}fil: { getframeinfo(cf.f_back).filename.split('/')[-1] }")