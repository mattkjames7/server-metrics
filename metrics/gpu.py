import subprocess
from .connectionCheck import connectionCheck
import re

gpuServerInfo = {}

def _listGpus(machine,settings):
    """
    List GPUs on a machine
    """
    global gpuServerInfo

    gpuSettings = settings.get("nvidia-gpu",{}).get(machine,None)

    if gpuSettings is None:
        return None
    
    if not "user" in gpuSettings or not "ip" in gpuSettings:
        return None

    ip = gpuSettings["ip"]
    user = gpuSettings["user"]

    if not connectionCheck(ip):
        print("Connection check failed")
        return None

    command = f"ssh {user}@{ip} 'nvidia-smi -L'"
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()
    output = output.decode().split("\n")
    gpuIds = [line.replace("GPU ","").split(":")[0] for line in output if line.startswith("GPU")]

    gpuServerInfo[machine] = gpuIds
    return gpuIds


def _decodeMem(output):
    """
    ==============NVSMI LOG==============

Timestamp                                 : Mon Mar  4 21:21:24 2024
Driver Version                            : 545.29.06
CUDA Version                              : 12.3

Attached GPUs                             : 1
GPU 00000000:06:10.0
    FB Memory Usage
        Total                             : 8192 MiB
        Reserved                          : 78 MiB
        Used                              : 8002 MiB
        Free                              : 111 MiB
    BAR1 Memory Usage
        Total                             : 256 MiB
        Used                              : 5 MiB
        Free                              : 251 MiB
    Conf Compute Protected Memory Usage
        Total                             : 0 MiB
        Used                              : 0 MiB
        Free                              : 0 MiB
    """
    lines = output.decode().split("\n")
    for i,line in enumerate(lines):
        if "FB Memory Usage" in line:
            break
    lines = lines[i+1:i+5]

    usage = None
    for line in lines:
        if "Used" in line:
            numbers = re.findall(r"\d+",line)
            if len(numbers) > 0:
                usage = int(numbers[0])

    return usage

def _decodeUtil(output):
    """
    
==============NVSMI LOG==============

Timestamp                                 : Mon Mar  4 21:22:01 2024
Driver Version                            : 545.29.06
CUDA Version                              : 12.3

Attached GPUs                             : 1
GPU 00000000:06:10.0
    Utilization
        Gpu                               : 99 %
        Memory                            : 74 %
        Encoder                           : 0 %
        Decoder                           : 0 %
        JPEG                              : N/A
        OFA                               : N/A
    GPU Utilization Samples
        Duration                          : 11.75 sec
        Number of Samples                 : 71
        Max                               : 99 %
        Min                               : 99 %
        Avg                               : 99 %
    Memory Utilization Samples
        Duration                          : 11.75 sec
        Number of Samples                 : 71
        Max                               : 75 %
        Min                               : 70 %
        Avg                               : 73 %
    ENC Utilization Samples
        Duration                          : 11.75 sec
        Number of Samples                 : 71
        Max                               : 0 %
        Min                               : 0 %
        Avg                               : 0 %
    DEC Utilization Samples
        Duration                          : 11.75 sec
        Number of Samples                 : 71
        Max                               : 0 %
        Min                               : 0 %
        Avg                               : 0 %


    """
    lines = output.decode().split("\n")
    for i,line in enumerate(lines):
        if "Utilization" in line:
            break
    lines = lines[i+1:i+5]

    util = None
    for line in lines:
        if "Gpu" in line:
            numbers = re.findall(r"\d+",line)
            if len(numbers) > 0:
                util = int(numbers[0])

    return util

def _decodeTemp(output):
    """

==============NVSMI LOG==============

Timestamp                                 : Mon Mar  4 21:23:06 2024
Driver Version                            : 545.29.06
CUDA Version                              : 12.3

Attached GPUs                             : 1
GPU 00000000:06:10.0
    Temperature
        GPU Current Temp                  : 82 C
        GPU T.Limit Temp                  : N/A
        GPU Shutdown Temp                 : 99 C
        GPU Slowdown Temp                 : 96 C
        GPU Max Operating Temp            : N/A
        GPU Target Temperature            : 83 C
        Memory Current Temp               : N/A
        Memory Max Operating Temp         : N/A

    """
    lines = output.decode().split("\n")
    for i,line in enumerate(lines):
        if "Temperature" in line:
            break
    lines = lines[i+1:i+5]

    temp = None
    for line in lines:
        if "GPU Current Temp" in line:
            numbers = re.findall(r"\d+",line)
            if len(numbers) > 0:
                temp = int(numbers[0])

    return temp


def _decodePow(output):
    """
    
==============NVSMI LOG==============

Timestamp                                 : Mon Mar  4 21:23:45 2024
Driver Version                            : 545.29.06
CUDA Version                              : 12.3

Attached GPUs                             : 1
GPU 00000000:06:10.0
    GPU Power Readings
        Power Draw                        : 131.68 W
        Current Power Limit               : 180.00 W
        Requested Power Limit             : 180.00 W
        Default Power Limit               : 180.00 W
        Min Power Limit                   : 90.00 W
        Max Power Limit                   : 217.00 W
    Power Samples
        Duration                          : 2.37 sec
        Number of Samples                 : 119
        Max                               : 150.76 W
        Min                               : 100.36 W
        Avg                               : 138.97 W
    GPU Memory Power Readings 
        Power Draw                        : N/A
    Module Power Readings
        Power Draw                        : N/A
        Current Power Limit               : N/A
        Requested Power Limit             : N/A
        Default Power Limit               : N/A
        Min Power Limit                   : N/A
        Max Power Limit                   : N/A

    """
    lines = output.decode().split("\n")
    for i,line in enumerate(lines):
        if "Power Readings" in line:
            break
    lines = lines[i+1:i+5]

    power = None
    for line in lines:
        if "Power Draw" in line:
            numbers = re.findall(r"[-+]?\d*\.?\d+",line)
            if len(numbers) > 0:
                power = float(numbers[0])

    return power

def _collectGpuStats(machine,gpu,settings):

    global gpuServerInfo

    if gpu not in gpuServerInfo.get(machine,[]):
        return None

    gpuSettings = settings.get("nvidia-gpu",{}).get(machine,None)

    if gpuSettings is None:
        return None
    
    if not "user" in gpuSettings or not "ip" in gpuSettings:
        return None

    ip = gpuSettings["ip"]
    user = gpuSettings["user"]


    commandFunctions = {
        "memory" : ("nvidia-smi -i 0 -q -d MEMORY",_decodeMem), 
        "power" : ("nvidia-smi -i 0 -q -d POWER",_decodePow),
        "util" : ("nvidia-smi -i 0 -q -d UTILIZATION",_decodeUtil),
        "temp" : ("nvidia-smi -i 0 -q -d TEMPERATURE",_decodeTemp),
    }

    data = {}
    for key in commandFunctions.keys():
        cmd, decoder = commandFunctions[key]
        command = f"ssh {user}@{ip} '{cmd}'"

        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()
        data[key] = decoder(output)

    return data

def getGpuMachine(machine,settings):

    global gpuServerInfo

    gpuIds = gpuServerInfo.get(machine,[])

    out = {}
    for gpuId in gpuIds:
        tmp = _collectGpuStats(machine,gpuId,settings)
        for k,v in tmp.items():
            out[f"{machine}-GPU{gpuId}-{k}"] = v

    return out


def getAllGpu(settings):

    global gpuServerInfo
    gpuSettings = settings.get("nvidia-gpu",{})

    machines = list(gpuSettings.keys())
    data = {}
    for machine in machines:
        if gpuServerInfo.get(machine,None) is None:
            _listGpus(machine,settings)
        
        tmp = getGpuMachine(machine,settings)
        if tmp != {}:
            data.update(tmp)
        
    return data
