# server-metrics

Collects metrics for servers/computers to be stored in an InfluxDB. By default, it will attempt to collect sensor information from `/sys/class/thermal` and `/sys/class/hwmon`. It also collects Nvidia GPU information using `pynvml`, eventually will probably use `rocm-smi` to collect AMD GPU data.

## Installation

### Ubuntu/Debian/Mint

Download the `.deb` package and install via apt:
```bash
sudo apt install ./server-metrics_x.y.z_amd64.deb`
```

### Fedora

Download the `.rpm` package and install using `dnf`:
```bash
sudo dnf install ./server-metrics-0.1.0-1.x86_64.rpm
```

### Others

Use the script:
```bash
sudo ./install.sh
```

## Uninstall

### Ubuntu/Debian/Mint

```bash
sudo apt remove server-metrics
```

### Fedora

```bash
sudo dnf remove server-metrics
```

### Others

```bash
sudo ./uninstall.sh
```

## Configuration

The configuration file is stored in `/etc/server-metrics/server-config.json`. The default configuration file **will not work** out of the box because the connection details for the influxDB intance need to be configured. To do so, edit the `influxdb` key of the config file:
```json
    "influxdb": {
        "token": "insert token here",
        "bucket": "bucket name",
        "url": "http://db.IP.address:8086",
        "host": "db IP address",
        "organization": "org name"
    }
```

By default, the configuration will attempt to find sensor for hwmon, thermals, nvidia GPUs and amd GPUs. To change this behavious, modify the following keys:
```json
    "amdgpu": true,
    "nvidiagpu": true,
    "hwmon": true,
    "thermal": true
```

It can also be configured to collect information from an IPMI device via SNMP (this has only been tested on an iDRAC 7) by configuring the `ipmi` key:
```json
    "ipmi": {
        "host": "192.168.0.20", # IPMI IP address
        "community": "public", # community name
        "objects": [ # list of objects to collect
            {
                "name": "Inlet Temp (°C)", # user defined label
                "oid": "iso.3.6.1.4.1.674.10892.5.4.700.20.1.6.1.1", # OID to collect (good luck with the documentation here...)
                "multiplier": 0.1 # Multiplies the value collected for the OID to convert to a real unit
            },
            ...
        ]
    }
```

Once the JSON has been configured, run `sudo systemctl restart server-metrics` to load it.

## Building Packages

### Deb

```bash
sudo apt-get update
sudo apt-get install ruby ruby-dev build-essential
gem install fpm
./build-deb.sh
```

### RPM

```bash
sudo dnf install ruby ruby-devel gcc make rpm-build python3 python3-setuptools
sudo gem install --no-document fpm
./build-rpm.sh
```

### Cleanup

Clean up all of the extra files created in either build case using
```bash
./clean.sh
```