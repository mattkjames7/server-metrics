import psutil

class PsutilTemps(object):
    def getTemps(self):

        # CPU usage: percentage utilization per CPU or overall
        cpuPercent = psutil.cpu_percent(interval=1)  # overall CPU usage over 1 second
        perCpu = psutil.cpu_percent(interval=1, percpu=True)  # list of per-CPU percentages

        # RAM usage: memory details
        memory = psutil.virtual_memory()
        ramUsed = memory.used
        ramTotal = memory.total
        ramPercent = memory.percent

        gb = 1024*1024*1024
        out = [
            {
                "name": "CPU Average (%)",
                "value": cpuPercent
            },
            {
                "name": "RAM Used (GB)",
                "value": ramUsed
            },
            {
                "name": "RAM Used (%)",
                "value": ramPercent
            },
            {
                "name": "RAM Total (GB)",
                "value": ramTotal
            }
        ]
        for i,cpu in enumerate(perCpu):
            out.append({
                "name": f"CPU {i} (%)",
                "value": cpu
            })

        return out