import os

THERMAL_PATH = '/sys/class/thermal'

def readFile(path):
    """Read the contents of a file and return it stripped of whitespace."""
    try:
        with open(path, 'r') as f:
            return f.read().strip()
    except Exception:
        return None

class ThermalTemps(object):



    def getSensorFriendlyName(self,sensorPath):
        """
        Try to determine a friendly name for the sensor.
        Some systems provide a 'name' file; otherwise, we fall back to the 'type' file.
        """
        # Some systems may have a 'name' file:
        name = readFile(os.path.join(sensorPath, 'name'))
        if name:
            return name

        # Fallback to the 'type' file:
        sensorType = readFile(os.path.join(sensorPath, 'type'))
        if sensorType:
            return sensorType

        # Otherwise, just return the directory name:
        return os.path.basename(sensorPath)
    


    def getTemps(self):
        if not os.path.exists(THERMAL_PATH):
            print(f"Path {THERMAL_PATH} does not exist.")
            return

        out = []
        for item in sorted(os.listdir(THERMAL_PATH)):
            itemPath = os.path.join(THERMAL_PATH, item)
            if os.path.isdir(itemPath):
                sensorName = self.getSensorFriendlyName(itemPath)

                # Iterate over all files (excluding the ones we already used)
                for fname in sorted(os.listdir(itemPath)):
                    if fname in ('type', 'name'):
                        continue
                    fpath = os.path.join(itemPath, fname)
                    if os.path.isfile(fpath):
                        content = readFile(fpath)
                        if content is None:
                            continue
                        # For temperature files, convert if appropriate:
                        if fname == 'temp':
                            try:
                                # Usually reported in millidegrees Celsius.
                                temp = int(content) / 1000.0
                                name = f"{sensorName} - {fname} - {temp}"
                                out.append({
                                    "name": name,
                                    "value": temp
                                })
                            except ValueError:
                                pass
                        else:
                            pass
        return out