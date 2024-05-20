from fastmqtt import FastMQTT

from npc_control_hub import ControlHub, PinID


async def main():
    fastmqtt = FastMQTT("mqtt.eclipse.org")

    # Start the cluster
    async with ControlHub(fastmqtt) as control_hub:
        update = await control_hub.update_pins(
            "ABCDE1234567", [PinID.INPUT_1, PinID.INPUT_2]
        ).wait_responce()

        print(update)
