import json
import os

def readConfig():

    home = os.getenv("HOME")
    configDir = f"{home}/.server-thermals"
    data = {}
    if os.path.isdir(configDir):
        fname = f"{configDir}/server-config.json"
        if os.path.isfile(fname):
            with open(fname,"r") as f:
                data = json.load(f)
            
    return data