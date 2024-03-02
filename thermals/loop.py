from time import time,sleep
from .readIdrac import readIdrac
from .settings import readSettings
from .upload import upload

def loop(period=60):

    settings = readSettings()

    while True:
        t0 = time()
        data = readIdrac(settings)
        upload(data,settings)
        t1 = time()
        
        dt = t1 - t0
        if dt < period:
            sleep(period - dt)
            