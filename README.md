
#  README.md for MQTT Device Cluster Module

  

##  Overview

  

The MQTT Device Cluster module is a comprehensive solution for managing MQTT communication with a variety of devices, especially focusing on pin configuration and state management in a clustered network environment. This Python module provides an easy-to-use interface for configuring and controlling device pins via MQTT, making it ideal for IoT applications.

  

##  Features

  

-  **MQTT Communication**: Leverage the MQTT protocol for efficient, real-time communication with a cluster of devices.

-  **Device Management**: Manage multiple devices in a clustered setup.

-  **Pin Configuration and Control**: Configure and control the state of pins on your devices.

-  **Asynchronous Communication**: Leverage asyncio for non-blocking MQTT communication.

-  **Flexible Callback Handling**: Use callback keys to handle specific device and pin updates.

-  **Error Handling and Reconnection Support**: Prepared to handle MQTT communication errors and reconnect as needed (TODO).

-  **Thread-safe Access**: Ensures thread-safe access to MQTT topics with a key-based locking mechanism.

  

##  Installation

  

### 1. Create a New SSH key

```bash

ssh-keygen  -t  rsa  -C  "GitHub_Mqtt_Device_Cluster"

```

The file should show up as ~/.ssh/GitHub_Mqtt_Device_Cluster and ~/.ssh/GitHub_Mqtt_Device_Cluster.pub

  

### 2. Create the SSH Configuration File

  

Next, use an editor to create a ~/.ssh/config file. Add the following contents.

```

Host GitHub_Mqtt_Device_Cluster

HostName github.com

IdentityFile ~/.ssh/GitHub_Mqtt_Device_Cluster

```

 

### 3. Install from private repo
####  If you use pip


```bash

pip  install  git+ssh://git@GitHub_Mqtt_Device_Cluster/naglyadservice/mqtt_device_cluster.git

```

  

GitHub_Mqtt_Device_Cluster here is Host in ~/.ssh/config file.

  
  

####  If you use Poetry

```bash

poetry  add  mqtt-device-cluster  --git  ssh://git@GitHub_Mqtt_Device_Cluster/naglyadservice/mqtt_device_cluster.git

```

  
  

##  Dependencies

  

- Python 3.7+

-  `aiomqtt` library for asynchronous MQTT communication.

  

Ensure that these dependencies are installed in your environment.

  

##  Usage

  

###  Basic Setup

  

```python

from mqtt_device_cluster import DeviceCluster, PinMode, PinState

import aiomqtt

  

# Initialize MQTT client and DeviceCluster

mqtt_client = aiomqtt.Client(...)

cluster =  DeviceCluster(mqtt_client)

  

# Start the cluster

async  with mqtt_client:

await cluster.start()

```

  

###  Configuring Pins

  

Configure the pins for a specific device:

  

```python

await device_cluster.config_pins(

device_id="device123",

pins=[

{"pin":  13,  "mode": PinMode.OUTPUT,  "state": PinState.HIGH},

{"pin":  14,  "mode": PinMode.OUTPUT,  "state": PinState.LOW},

],

)

```

  

###  Setting Pin States

  

Set the state of pins for a device:

  

```python

updates =  await device_cluster.set_pins(

device_id="device123",

pins=[

{"pin":  13,  "state": PinState.LOW,  "time":  500},

{"pin":  14,  "state": PinState.HIGH,  "time":  500},

],

)

print(updates)

```

  

###  Requesting Pin Updates

  

Request updates for specific pins of a device:

  

```python

updates =  await device_cluster.update(

device_id="device123",

pins=[13,  14],

timeout=5

)

print(updates)

```

  

##  Modules

  

-  `DeviceCluster`: Main class for managing MQTT communication and device pin configurations.

-  `PinMode`, `PinState`: Enum constants for defining pin modes and states.

-  `ConfigPin`, `SetPin`: Typed dictionaries for pin configuration and setting.

-  `PinCache`: Dataclass for caching pin states.

-  `CbKey`: Dataclass for managing callback keys.

-  `KeyLock`: A class for managing asynchronous locks.

  

##  Documentation

  

For detailed API documentation, refer to the docstrings within each class and method in the module.