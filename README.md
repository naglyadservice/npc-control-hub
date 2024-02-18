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

### Basic Setup

```python
import aiomqtt
from mqtt_device_cluster import DeviceCluster, PinState, Pin

# Initialize MQTT client and DeviceCluster
mqtt_client = aiomqtt.Client(...)
cluster = DeviceCluster(mqtt_client)

# Start the cluster
async with mqtt_client:
    await cluster.start()
```


### Setting Pin States

```python
updates = await cluster.set_pins(
    "ABCDE1234567",
    [
        {"pin": Pin.RELAY_1, "state": PinState.LOW},
        {"pin": Pin.RELAY_2, "state": PinState.HIGH, "time": 1000},
    ],
).wait_responce()
print(updates)
```

## or do not wait for controller responce
```python
await cluster.set_pins(
    "ABCDE1234567",
    [
        {"pin": Pin.RELAY_1, "state": PinState.LOW},
        {"pin": Pin.RELAY_2, "state": PinState.HIGH, "time": 1000},
    ],
)
```

### Requesting Pin Updates

Request updates for specific pins of a device:

```python
updates = await cluster.update_pins(
    "C89FABE0F908", [Pin.RELAY_1, Pin.RELAY_2]
).wait_responce()
print(updates)
```

### Waiting for Specific Pin Update

The `wait_for` method allows you to asynchronously wait for updates to specific pins, specified by filters.

```python
# Define callback keys for the pins you want to monitor
filters = [
    CallbackFilter(pin=Pin.INPUT_1, state=PinState.HIGH),
    CallbackFilter(pin=Pin.RELAY_1, state=PinState.LOW),
]

# Wait for the specified pin updates
updates = await cluster.wait_for("C89FABE0F908", filters)

# Process the updates
for update in updates:
    print(f"Pin {update.pin} updated to {update.state}")
```

### Adding Update Callbacks
The `add_update_callback` method allows you to add a callback function that gets called whenever there's an update to any pin's state. 

```python
async def pin_update_callback(device_id: str, updates: list[Update]):
    for update in updates:
        print(f"Pin {update.pin} on device {device_id} updated to {update.state}")

# Add the callback to the DeviceCluster
cluster.add_update_callback(pin_update_callback)

# The callback will now be called for all updates
# Also you can remoce callback
cluster.remove_update_callback(pin_update_callback)


```

## Documentation

For detailed API documentation, refer to the docstrings within each class and method in the module.