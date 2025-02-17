from pynvml import (
    nvmlInit,
    nvmlShutdown,
    nvmlDeviceGetCount,
    nvmlDeviceGetHandleByIndex,
    nvmlDeviceGetName,
    nvmlDeviceGetTemperature,
    nvmlDeviceGetFanSpeed,
    nvmlDeviceGetPowerUsage,
    nvmlDeviceGetUtilizationRates,
    nvmlDeviceGetMemoryInfo,
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
                    "name": f"{name} - Temp (C)",
                    "value": temp
                })
            except NVMLError:
                pass

            try:
                fanSpeed = nvmlDeviceGetFanSpeed(handle)
                out.append({
                    "name": f"{name} - Fan (%)",
                    "value": fanSpeed
                })
            except NVMLError:
                pass

            try:
                power = nvmlDeviceGetPowerUsage(handle)/1000.0
                out.append({
                    "name": f"{name} - Power (W)",
                    "value": power
                })
            except NVMLError:
                pass

            try:
                mem = nvmlDeviceGetMemoryInfo(handle)
                gb = 1024*1024*1024
                out.extend([
                    {
                        "name": f"{name} - Memory Total (GB)",
                        "value": mem.total/gb
                    },{
                        "name": f"{name} - Memory Free (GB)",
                        "value": mem.free/gb
                    },{
                        "name": f"{name} - Memory Used (GB)",
                        "value": mem.used/gb
                    },
                ])
            except NVMLError:
                pass

            try:
                util = nvmlDeviceGetUtilizationRates(handle)
                gb = 1024*1024*1024
                out.extend([
                    {
                        "name": f"{name} - GPU Util (%)",
                        "value": util.gpu
                    },{
                        "name": f"{name} - Memory Use (%)",
                        "value": util.memory
                    }
                ])
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
