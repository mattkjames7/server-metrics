from .config import readConfig
from .ipmi import IPMITemps
from .amdgpu import AmdgpuTemps
from .nvidia import NvidiaTemps
from .hwmon import HwMonTemps
from .thermal import ThermalTemps

def main():

    config = readConfig()
    dbConfig = config["influxdb"]

    sensors = []
    if "ipmi" in config:
        sensors.append(IPMITemps(config["ipmi"]))
    sensors.append(AmdgpuTemps())
    sensors.append(NvidiaTemps())
    sensors.append(HwMonTemps())
    sensors.append(ThermalTemps())

