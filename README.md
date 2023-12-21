# README.md for MQTT Device Cluster Module

## Overview

The MQTT Device Cluster module is a comprehensive solution for managing MQTT communication with a variety of devices, especially focusing on pin configuration and state management in a clustered network environment. This Python module provides an easy-to-use interface for configuring and controlling device pins via MQTT, making it ideal for IoT applications.

## Features

- **MQTT Communication**: Leverage the MQTT protocol for efficient, real-time communication with a cluster of devices.
- **Device Management**: Manage multiple devices in a clustered setup.
- **Pin Configuration and Control**: Configure and control the state of pins on your devices.
- **Asynchronous Communication**: Leverage asyncio for non-blocking MQTT communication.
- **Flexible Callback Handling**: Use callback keys to handle specific device and pin updates.
- **Error Handling and Reconnection Support**: Prepared to handle MQTT communication errors and reconnect as needed (TODO).
- **Thread-safe Access**: Ensures thread-safe access to MQTT topics with a key-based locking mechanism.

## Installation

### Using Pip

If you're using pip, you need to have access to the private repository. You can install the package directly from the repository URL. Replace `YOUR_GIT_REPO_URL` with the actual URL of your private repository.

```bash
pip install git+YOUR_GIT_REPO_URL
```

Example:

```bash
pip install git+https://github.com/username/mqtt-device-cluster.git
```

### Using Poetry

For Poetry, you need to add the private repository to your `pyproject.toml` and then specify the dependency.

1. Add the private repository:

   ```toml
   [[tool.poetry.source]]
   name = "private-repo"
   url = "YOUR_GIT_REPO_URL"
   ```

2. Specify the module as a dependency:

   ```toml
   [tool.poetry.dependencies]
   mqtt-device-cluster = { version = "*", source = "private-repo" }
   ```

3. Install the dependencies:

   ```bash
   poetry install
   ```

## Dependencies

- Python 3.7+
- `aiomqtt` library for asynchronous MQTT communication.

Ensure that these dependencies are installed in your environment.

## Usage

### Basic Setup

```python
from mqtt_device_cluster import DeviceCluster, PinMode, PinState
import aiomqtt

# Initialize MQTT client and DeviceCluster
mqtt_client = aiomqtt.Client(...)
cluster = DeviceCluster(mqtt_client)

# Start the cluster
async with mqtt_client:
    await cluster.start()
```

### Configuring Pins

Configure the pins for a specific device:

```python
await device_cluster.config_pins(
    device_id="device123",
    pins=[
        {"pin": 13, "mode": PinMode.OUTPUT, "state": PinState.HIGH},
        {"pin": 14, "mode": PinMode.OUTPUT, "state": PinState.LOW},
    ],
)
```

### Setting Pin States

Set the state of pins for a device:

```python
updates = await device_cluster.set_pins(
    device_id="device123",
    pins=[
        {"pin": 13, "state": PinState.LOW, "time": 500},
        {"pin": 14, "state": PinState.HIGH, "time": 500},
    ],
)
print(updates)
```

### Requesting Pin Updates

Request updates for specific pins of a device:

```python
updates = await device_cluster.update(
    device_id="device123",
    pins=[13, 14],
    timeout=5
)
print(updates)
```

## Modules

- `DeviceCluster`: Main class for managing MQTT communication and device pin configurations.
- `PinMode`, `PinState`: Enum constants for defining pin modes and states.
- `ConfigPin`, `SetPin`: Typed dictionaries for pin configuration and setting.
- `PinCache`: Dataclass for caching pin states.
- `CbKey`: Dataclass for managing callback keys.
- `KeyLock`: A class for managing asynchronous locks.

## Documentation

For detailed API documentation, refer to the docstrings within each class and method in the module.