import pytest
from fastmqtt import FastMQTT

from npc_control_hub import ControlHub


@pytest.fixture(scope="session")
def device_id():
    return "test_device"


@pytest.fixture(scope="session")
# async def control_hub(mosquitto: tuple[str, int]):
async def control_hub():
    fastmqtt = FastMQTT("test.mosquitto.org")
    async with ControlHub(fastmqtt) as control_hub:
        yield control_hub
