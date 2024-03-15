from fastmqtt import FastMQTT

from mqtt_device_cluster import DeviceCluster, PinID


async def main():
    fastmqtt = FastMQTT("mqtt.eclipse.org")
    cluster = DeviceCluster(fastmqtt)

    # Start the cluster
    async with fastmqtt:
        update = await cluster.update_pins(
            "ABCDE1234567", [PinID.INPUT_1, PinID.INPUT_2]
        ).wait_responce()

        print(update)
