import asyncio
import logging

import aiomqtt

from mqtt_device_cluster import DeviceCluster, PinState


async def main():
    logging.basicConfig(level=logging.DEBUG)
    device_id = "544B3B144B8C"
    led_pin = 13
    relay_pin = 25
    hostname = "broker.emqx.io"
    port = 1883
    username = None
    password = None
    client_id = None

    mqtt = aiomqtt.Client(
        hostname=hostname,
        port=port,
        username=username,
        password=password,
        client_id=client_id,
    )
    async with mqtt:
        controller = DeviceCluster(mqtt)

        ########## One time setup at start ##########
        await controller.start()
        # await controller.config_pins(
        #     device_id,
        #     pins=[
        #         {"pin": led_pin, "mode": PinMode.OUTPUT, "state": PinState.HIGH},
        #         {"pin": relay_pin, "mode": PinMode.OUTPUT, "state": PinState.LOW},
        #     ],
        # )
        ########## ----------------------- ##########

        # Open the gate
        updates = await controller.set_pins(
            device_id,  # Device ID
            pins=[
                {"pin": led_pin, "state": PinState.LOW, "time": 500},
                {"pin": relay_pin, "state": PinState.HIGH, "time": 500},
            ],
        )

        print(updates)


if __name__ == "__main__":
    asyncio.run(main())
