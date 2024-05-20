# README.md for NPC Control Hub

## Overview

The NPC Control Hub is a comprehensive solution for managing MQTT communication with a variety of devices, especially focusing on pin configuration and state management in a clustered network environment. This Python module provides an easy-to-use interface for controlling device pins via MQTT.

## Features

- **MQTT Communication**
- **Device Management**
- **Pin read and write**
- **Asynchronous Communication**
- **Flexible Callback Handling**
- **Thread-safe Access**:

## Installation
#### If you use pip

```bash
pip install git+ssh://git@github.com/naglyadservice/npc-control-hub.git
```

#### If you use Poetry
```bash
poetry add myprivaterepo --git ssh://git@github.co/naglyadservice/npc-control-hub.git
```
## Usage
### Setting Pin States

```python
from fastmqtt import FastMQTT

from npc_control_hub import ControlHub, PinID


async def main():
    fastmqtt = FastMQTT("mqtt.eclipse.org")

    # Start the cluster
    async with ControlHub(fastmqtt) as control_hub:
        update = await control_hub.update_pins(
            "ABCDE1234567", [PinID.INPUT_1, PinID.INPUT_2]
        ).wait_responce()

        print(update)

```

## More examples see in repo

## Documentation

For detailed API documentation, refer to the docstrings within each class and method in the module.