import asyncio

from fastmqtt import FastMQTT

from mqtt_device_cluster import (
    CallbackFilter,
    DeviceCluster,
    PinID,
    PinState,
)


async def main():
    fastmqtt = FastMQTT("mqtt.eclipse.org")
    cluster = DeviceCluster(fastmqtt)

    # Start the cluster
    async with fastmqtt:
        filters = [
            CallbackFilter(id=PinID.INPUT_1, state=PinState.HIGH),
            CallbackFilter(id=PinID.RELAY_1, state=PinState.LOW),
        ]

        updates = await cluster.wait_for("C89FABE0F908", filters)
        for update in updates:
            print(f"Pin {update.id} updated to {update.state}")


if __name__ == "__main__":
    asyncio.run(main())
