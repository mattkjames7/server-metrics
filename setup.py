from setuptools import setup, find_packages

def getVersion():
    with open("thermals/__init__.py") as f:
        lines = f.readlines()
    version = "0.0.0"
    for line in lines:
        if "__version__" in line:
            s = line.split("=")
            version = s[1].strip().replace("\"","")
    return version

setup(
    name="server-thermals",
    version=getVersion(),
    packages=find_packages(),
    install_requires=[
        "pynvml",
        "easysnmp",
        "influxdb-client"
    ],
    entry_points={
        "console_scripts": [
            "server-thermals = thermals:main",
        ],
    },
)
