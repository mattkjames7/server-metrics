from easysnmp import Session, EasySNMPError, EasySNMPTimeoutError

class IPMITemps(object):
    def __init__(self,data):
        """
        data should be of the following format
        {
            "host": "IP address",
            "community": "public",
            "objects": [
                {
                    "name": "sensor name",
                    "oid": "iso.3.6.1.3.4.5.3....",
                    "multiplier": 0.1
                }
            ]
        }
        """
        self.host = data["host"]
        self.community = data["community"]
        self.objects = data["objects"]

    def getTemps(self):

        try:
            # Initialize the SNMP session using SNMP version 2.
            session = Session(
                hostname=self.host,
                community=self.community,
                version=2,  
                timeout=5,
                retries=3
            )
        except:
            return []
        
        out = []
        for object in self.objects:
            try:
                obj = session.get(object["oid"])
                value = obj.value*object.get("multiplier",1.0)
                out.append({
                    "name": obj["name"],
                    "value": value
                })
            except:
                pass
            
        return out