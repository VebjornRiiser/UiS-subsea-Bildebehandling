#!/usr/bin/python3.8
# -*- coding: UTF-8 -*-

import dataset
import time
import subprocess
import json
from datetime import datetime

db = dataset.connect('postgresql://postgres:postgres@127.0.0.1:5432/postgres')
table = db['sensors']
corespeed = db['corespeed']
cpuusage = db['cpuusage']

def run_log():
    # CPU bruk
    cpu_bruk_out = subprocess.check_output("mpstat -P ALL 1 1 -o JSON", shell=True).decode('utf-8')
    cpu_bruk_liste = json.loads(cpu_bruk_out)["sysstat"]["hosts"][0]["statistics"][0]["cpu-load"]
    tid = int(time.time())
    for cpu in cpu_bruk_liste:
        cpu["time"] = tid
        cpuusage.insert(cpu)

    # per core fart
    cpu_fart = subprocess.check_output('cat /proc/cpuinfo | grep "cpu MHz"', shell=True).decode('utf-8')
    cpu_liste = [float(i.split()[3]) for i in cpu_fart.split("\n")[:-1]]
    cpu_data = dict( zip( [f"core{i}" for i in range(len(cpu_liste))], cpu_liste ), time=tid )
    corespeed.insert( cpu_data )

    # Coretemp + vcore
    out = subprocess.check_output("sensors", shell=True).decode('utf-8')
    out = out.split("\n")
    coreVolt = out[6].split()[1]
    temp = out[8].split()[1][:-2]
    data = dict(time=tid, temp=float(temp), vcore=float(coreVolt))
    #print(data)
    table.insert( data )

while True:
    run_log()
    time.sleep(0.2)
