import asyncio

from fastmqtt import FastMQTT

from npc_control_hub import ControlHub, PinID, PinState


async def main():
    fastmqtt = FastMQTT("mqtt.eclipse.org")

    async with ControlHub(fastmqtt) as control_hub:
        await control_hub.set_pins(
            "ABCDE1234567",
            [
                {"pin": PinID.RELAY_1, "state": PinState.LOW},
                {"pin": PinID.RELAY_2, "state": PinState.HIGH, "time": 1000},
            ],
        )


if __name__ == "__main__":
    asyncio.run(main())
