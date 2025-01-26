from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime

def upload(data,settings):

    jsonBody = [
        {
            "measurement" : "server_metrics",
            "fields" : data
        }
    ]

    dbsettings = settings["influxdb"]

    client = InfluxDBClient(
        dbsettings["url"],
        dbsettings["token"],
        dbsettings["organization"]
    )

    #point = Point("server_metrics").tag("host", "server1").field(data).time(datetime.utcnow(), WritePrecision.NS)
    point = Point("server_metrics").tag("host", dbsettings["host"]).time(datetime.utcnow(), WritePrecision.NS)
    for key, value in data.items():
        point.field(key, value)

    write_api = client.write_api(write_options=SYNCHRONOUS)
    write_api.write(bucket=dbsettings["bucket"], org=dbsettings["organization"], record=point)

    # Close the client
    client.close()

def uploadGpu(data,machine,settings):


    dbsettings = settings["influxdb"]

    client = InfluxDBClient(
        dbsettings["url"],
        dbsettings["token"],
        dbsettings["organization"]
    )

    point = Point("gpu_metrics").tag("host", machine).time(datetime.utcnow(), WritePrecision.NS)
    for key, value in data.items():
        point.field(key, value)

    write_api = client.write_api(write_options=SYNCHRONOUS)
    write_api.write(bucket=dbsettings["bucket"], org=dbsettings["organization"], record=point)

    # Close the client
    client.close()