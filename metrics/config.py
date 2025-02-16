import json
import os

def readConfig():
    """
    data should have the following structure

    {
        "period": 10, # sampling period in seconds (optional)
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

    data = {}
    
    fname = "/etc/server-metrics/server-config.json"
    if os.path.isfile(fname):
        with open(fname,"r") as f:
            data = json.load(f)
            
    return data