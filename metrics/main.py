from .config import readConfig
from .ipmi import IPMITemps
from .amdgpu import AmdgpuTemps
from .nvidia import NvidiaTemps
from .hwmon import HwMonTemps
from .thermal import ThermalTemps
from .upload import uploadMetrics
import subprocess
from time import time,sleep

def main():

    hostname = subprocess.run(
        ["hostname"],
        capture_output=True,
        text=True
    ).stdout.strip()

    config = readConfig()
    period = config.get("period",10)
    sensors = []
    if "ipmi" in config:
        ipmi = IPMITemps(config["ipmi"])
    else:
        ipmi = None
    if config.get("amdgpu",True):
        sensors.append(AmdgpuTemps())
    if config.get("nvidiagpu",True):
        sensors.append(NvidiaTemps())
    if config.get("hwmon",True):
        sensors.append(HwMonTemps())
    if config.get("thermal",True):
        sensors.append(ThermalTemps())

    while True:
        t0 = time()

        results = []
        for sensor in sensors:
            results.extend(sensor.getTemps())

        dbdata = {f"{hostname}: {result['name']}":result["value"] for result in results}
        if ipmi is not None:
            results = ipmi.getTemps()
            label = f"IPMI-{config['ipmi']['host']}"
            for result in results:
                dbdata[f"{label} {result['name']}"] = result["value"]
        
        dbdata = {k.replace(" ","_"):v for k,v in dbdata.items()}
        uploadMetrics(dbdata,config)
        t1 = time()
        
        dt = t1 - t0
        if dt < period:
            sleep(period - dt)