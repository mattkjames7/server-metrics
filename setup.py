from setuptools import setup, find_packages

setup(
    name="server-thermals",
    version="0.1.0",
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
