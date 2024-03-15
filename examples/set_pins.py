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
