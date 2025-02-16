import os
import re

class HwMonTemps(object):
    def getTemps(self):
        """
        Scans the /sys/class/hwmon interface and collects temperature sensor readings.
        
        Returns:
            A dictionary where keys are chip names (from the 'name' file) and
            values are lists of tuples: (sensorLabel, temperature_in_celsius).
        """
        hwmonPath = '/sys/class/hwmon'
        sensors = []

        if not os.path.exists(hwmonPath):
            return sensors

        # Iterate over each hwmon device directory
        for hwmonDir in os.listdir(hwmonPath):
            devicePath = os.path.join(hwmonPath, hwmonDir)
            if not os.path.isdir(devicePath):
                continue

            # Try to get the chip name from the 'name' file
            chipFile = os.path.join(devicePath, 'name')
            if os.path.isfile(chipFile):
                try:
                    with open(chipFile, 'r') as f:
                        chipName = f.read().strip()
                except Exception:
                    chipName = hwmonDir
            else:
                chipName = hwmonDir

            sensorReadings = []

            # Look for files matching temp<num>_input
            for fname in os.listdir(devicePath):
                match = re.match(r'temp(\d+)_input', fname)
                if match:
                    sensorNum = match.group(1)
                    inputFile = os.path.join(devicePath, fname)
                    try:
                        with open(inputFile, 'r') as f:
                            # Temperature is usually reported in millidegrees Celsius.
                            tempraw = int(f.read().strip())
                            tempc = tempraw / 1000.0
                    except Exception:
                        continue

                    # Attempt to get a sensor label (if available)
                    labelFile = os.path.join(devicePath, f'temp{sensorNum}_label')
                    if os.path.isfile(labelFile):
                        try:
                            with open(labelFile, 'r') as f:
                                sensorLabel = f.read().strip()
                        except Exception:
                            sensorLabel = f'temp{sensorNum}'
                    else:
                        sensorLabel = f'temp{sensorNum}'

                    sensorReadings.append({
                        "name": f"{chipName} - {sensorLabel}", 
                        "value": tempc
                    })


        return sensors
