# README.md for MQTT Device Cluster Module

## Overview

The MQTT Device Cluster module is a comprehensive solution for managing MQTT communication with a variety of devices, especially focusing on pin configuration and state management in a clustered network environment. This Python module provides an easy-to-use interface for controlling device pins via MQTT.

## Features

- **MQTT Communication**
- **Device Management**
- **Pin read and write**
- **Asynchronous Communication**
- **Flexible Callback Handling**
- **Thread-safe Access**:

## Installation

### 1. Create a New SSH key
```bash
ssh-keygen -t rsa -C "GitHub_Mqtt_Device_Cluster"
```
The file should show up as ~/.ssh/GitHub_Mqtt_Device_Cluster and ~/.ssh/GitHub_Mqtt_Device_Cluster.pub

### 2. Add deployleys
add ~/.ssh/GitHub_Mqtt_Device_Cluster.pub ro deploykeys of repo [more here](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/managing-deploy-keys#set-up-deploy-keys).

### 3. Create the SSH Configuration File

Next, use an editor to create a ~/.ssh/config file. Add the following contents.
```
Host GitHub_Mqtt_Device_Cluster
  HostName github.com
  IdentityFile ~/.ssh/GitHub_Mqtt_Device_Cluster
```

### 4. Install:

#### If you use pip

```bash
pip install git+ssh://git@GitHub_Mqtt_Device_Cluster/naglyadservice/mqtt_device_cluster.git
```

GitHub_Mqtt_Device_Cluster here is Host in  ~/.ssh/config file.


#### If you use Poetry
```bash
poetry add myprivaterepo --git ssh://git@GitHub_Mqtt_Device_Cluster/naglyadservice/mqtt_device_cluster.git
```
## Usage
### Setting Pin States

```python
import asyncio

from fastmqtt import FastMQTT

from mqtt_device_cluster import DeviceCluster, PinID, PinState


async def main():
    fastmqtt = FastMQTT("mqtt.eclipse.org")
    cluster = DeviceCluster(fastmqtt)

    async with fastmqtt:
        await cluster.set_pins(
            "ABCDE1234567",
            [
                {"pin": PinID.RELAY_1, "state": PinState.LOW},
                {"pin": PinID.RELAY_2, "state": PinState.HIGH, "time": 1000},
            ],
        )


if __name__ == "__main__":
    asyncio.run(main())

```

## More examples see in repo

## Documentation

For detailed API documentation, refer to the docstrings within each class and method in the module.