import asyncio

from fastmqtt import FastMQTT

from npc_control_hub import ControlHub, PinID


async def main():
    async with FastMQTT("mqtt.eclipse.org") as fastmqtt:
        async with ControlHub(fastmqtt) as control_hub:
            update = await control_hub.update_pins(
                "ABCDE1234567", [PinID.INPUT_1, PinID.INPUT_2]
            ).wait_responce()

        print(update)


if __name__ == "__main__":
    asyncio.run(main())
