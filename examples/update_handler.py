import asyncio

from fastmqtt import FastMQTT

from npc_control_hub import ControlHub, RawUpdate


async def main():
    async with FastMQTT("mqtt.eclipse.org") as fastmqtt:
        async with ControlHub(fastmqtt) as control_hub:

            async def pin_update_callback(device_id: str, update: RawUpdate):
                print(f"Got update from {device_id}: {update}")

            # Add the callback to the ControlHub
            control_hub.add_update_callback(pin_update_callback)
            await asyncio.sleep(10)
            # Also you can remoce callback
            control_hub.remove_update_callback(pin_update_callback)


if __name__ == "__main__":
    asyncio.run(main())
