from inspect import currentframe

# Print info om nåværende linje.
def ln():
    cf = currentframe()
    print(f"Linjenummer: {cf.f_back.f_lineno} er nådd")