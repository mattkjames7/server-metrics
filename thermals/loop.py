from time import time,sleep
from .readIdrac import readIdrac
from .settings import readSettings
from .upload import upload,uploadGpu
from .gpu import _listGpus,getGpuMachine,gpuServerInfo

def loop(period=60):

    settings = readSettings()

    while True:
        t0 = time()
        try:
            data = readIdrac(settings)
            upload(data,settings)
        except Exception as e:
            print("Upload Failed")
            t01 = time.time()
            sleep(0.5*(period - (t01 - t1)))
            try:
                data = readIdrac(settings)
                upload(data,settings)                
            except:
                print("Failed Retry")

        t1 = time()
        
        dt = t1 - t0
        if dt < period:
            sleep(period - dt)
            

def loopGpu(period=60):

    settings = readSettings()
    gpuSettings = settings.get("nvidia-gpu",{})

    machines = list(gpuSettings.keys())

    while True:
        t0 = time()
        for machine in machines:


            try:
                if gpuServerInfo.get(machine,None) is None:
                    _listGpus(machine,settings)
                data = getGpuMachine(machine,settings)
                if data != {}:
                    uploadGpu(data,machine,settings)
            except Exception as e:
                print(f"Upload Failed For {machine}")


        t1 = time()
        
        dt = t1 - t0
        if dt < period:
            sleep(period - dt)
            