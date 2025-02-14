import json
import os

def readConfig():
    """
    data should have the following structure

    {
        "influxdb": {
            "url": "url to database",
            "token": "access token",
            "organization": "organization name",
            "host": "IP to host",
            "bucket": "bucket name"
        },
        "ipmi": see `ipmi.py` for structure
    }
    
    """
    home = os.getenv("HOME")
    configDir = f"{home}/.server-thermals"
    data = {}
    if os.path.isdir(configDir):
        fname = f"{configDir}/server-config.json"
        if os.path.isfile(fname):
            with open(fname,"r") as f:
                data = json.load(f)
            
    return data