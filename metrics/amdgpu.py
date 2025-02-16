
import subprocess
import json

def isAmdGpuPresent():
    """
    Checks if an AMD (or ATI) GPU is present on the system by parsing the output of `lspci`.

    Returns:
        True if an AMD/ATI GPU is found, False otherwise.
    """
    try:
        result = subprocess.run(["lspci"], stdout=subprocess.PIPE, text=True, check=True)
        for line in result.stdout.splitlines():
            if "VGA" in line and ("AMD" in line or "ATI" in line):
                return True
    except Exception as e:
        print(f"Error running lspci: {e}")
    return False


class AmdgpuTemps(object):
    def __init__(self):

        if isAmdGpuPresent():
            self.getTemps = self._getTemps
        else:
            self.getTemps = self._dummy

    def _dummy(self):
        return []
    
    def _getTemps(self):
        try:
            # The --json flag might be available to get JSON output (depending on version).
            result = subprocess.run(['rocm-smi', '--json'], capture_output=True, text=True)
            if result.returncode != 0:
                print("rocm-smi error:", result.stderr)
                return {}
            data = json.loads(result.stdout)
            # The exact parsing depends on the output structure.
            return []
        except Exception as e:
            print("Error calling rocm-smi:", e)
            return []