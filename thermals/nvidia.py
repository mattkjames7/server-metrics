from pynvml import (
    nvmlInit,
    nvmlShutdown,
    nvmlDeviceGetCount,
    nvmlDeviceGetHandleByIndex,
    nvmlDeviceGetName,
    nvmlDeviceGetTemperature,
    nvmlDeviceGetFanSpeed,
    NVML_TEMPERATURE_GPU,
    NVMLError,
)



class NvidiaTemps(object):
    def __init__(self):

        try:
            nvmlInit()
            self.devices = nvmlDeviceGetCount()
            self.getTemps = self._getTemps
        except:
            self.getTemps = self._dummy
        
    def _getTemps(self):

        out = []

        for device in range(self.devices):
            handle = nvmlDeviceGetHandleByIndex(device)
            name = nvmlDeviceGetName()
            try:
                temp = nvmlDeviceGetTemperature(handle, NVML_TEMPERATURE_GPU)
                out.append({
                    "name": f"{name} - Temp",
                    "value": temp
                })
            except NVMLError:
                pass

            try:
                fanSpeed = nvmlDeviceGetFanSpeed(handle)
                out.append({
                    "name": f"{name} - Fan",
                    "value": fanSpeed
                })
            except NVMLError:
                pass

        return out

    def _dummy(self):
        return []
    
    def __del__(self):
        try:
            nvmlShutdown()
        except NVMLError:
            pass
