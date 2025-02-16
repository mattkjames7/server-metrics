import json

def readSettings():

    filename = "settings.cfg"

    with open(filename,"r") as f:
        return json.load(f)
    
    