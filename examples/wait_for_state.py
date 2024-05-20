import asyncio

from fastmqtt import FastMQTT

from npc_control_hub import (
    CallbackFilter,
    ControlHub,
    PinID,
    PinState,
)


async def main():
    fastmqtt = FastMQTT("mqtt.eclipse.org")

    # Start the cluster
    async with ControlHub(fastmqtt) as control_hub:
        filters = [
            CallbackFilter(id=PinID.INPUT_1, state=PinState.HIGH),
            CallbackFilter(id=PinID.RELAY_1, state=PinState.LOW),
        ]

        updates = await control_hub.wait_for("C89FABE0F908", filters)
        for update in updates:
            print(f"Pin {update.id} updated to {update.state}")


if __name__ == "__main__":
    asyncio.run(main())
