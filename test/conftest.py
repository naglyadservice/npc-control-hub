import pytest
from fastmqtt import FastMQTT

from mqtt_device_cluster import DeviceCluster


@pytest.fixture(scope="session")
def device_id():
    return "test_device"


@pytest.fixture(scope="session")
async def device_cluster(mosquitto: tuple[str, int]):
    fastmqtt = FastMQTT(mosquitto[0], int(mosquitto[1]))
    device_cluster = DeviceCluster(fastmqtt)
    async with fastmqtt:
        yield device_cluster
