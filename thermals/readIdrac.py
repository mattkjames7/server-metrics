import numpy as np
import subprocess
import re

def _findLine(start,output):

    out = []
    for line in output:
        if line.startswith(start):
            out.append(line)

    return out

def _extractTemps(s):

    matches = re.findall(r"[-+]?\d+C",s)

    temps = [int(match.lower().replace("c","")) for match in matches]
    return temps

def _extractFanSpeed(s):

    rpmMatch = re.findall(r"\d+RPM",s)
    rpm = int(rpmMatch[0].replace("RPM",""))

    percMatch = re.findall(r"\d+%",s)
    perc = int(percMatch[-1].replace("%",""))

    return rpm,perc

def _extractPower(s):

    powerMatch = re.findall(r"\d+Watts",s)
    power = int(powerMatch[0].replace("Watts",""))
    return power

def _decodeOutput(output):

    output = output.decode().split("\n")

    out = {}

    #temperatures
    line = _findLine("System Board Inlet Temp",output)[0]
    out["Inlet-Temp"] = _extractTemps(line)[0]

    line = _findLine("System Board Exhaust Temp",output)[0]
    out["Exhaust-Temp"] = _extractTemps(line)[0]

    line = _findLine("CPU1 Temp",output)[0]
    out["CPU1-Temp"] = _extractTemps(line)[0]
    
    line = _findLine("CPU2 Temp",output)[0]
    out["CPU2-Temp"] = _extractTemps(line)[0]

    # Fans
    fanLines = _findLine("System Board Fan",output)
    fanLines = [line for line in fanLines if not "Redundancy" in line]

    fanNums = [int(line.split()[2].replace("Fan","")) for line in fanLines]
    for no,line in zip(fanNums,fanLines):
        out[f"Fan{no}-RPM"],out[f"Fan{no}-Perc"] = _extractFanSpeed(line)
    
    # power
    line = _findLine("System Board Pwr Consumption",output)[0]
    out["Power"] = _extractPower(line)

    return out



def readIdrac(settings):

    idracSettings = settings["idrac"]
    user = idracSettings["user"]
    ip = idracSettings["ip"]

    command = f"ssh {user}@{ip} 'racadm getsensorinfo'"
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()

    return _decodeOutput(output)