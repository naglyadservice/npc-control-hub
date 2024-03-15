import asyncio

from fastmqtt import FastMQTT

from mqtt_device_cluster import DeviceCluster, RawUpdate


async def main():
    fastmqtt = FastMQTT("mqtt.eclipse.org")
    cluster = DeviceCluster(fastmqtt)

    async with fastmqtt:

        async def pin_update_callback(device_id: str, update: RawUpdate):
            print(f"Got update from {device_id}: {update}")

        # Add the callback to the DeviceCluster
        cluster.add_update_callback(pin_update_callback)
        await asyncio.sleep(10)
        # Also you can remoce callback
        cluster.remove_update_callback(pin_update_callback)


if __name__ == "__main__":
    asyncio.run(main())
