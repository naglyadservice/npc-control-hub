import json
import asyncio
import pytest
from fastmqtt import Message

from mqtt_device_cluster import DeviceCluster, PinID, PinMode, PinState, VoiceCallState


@pytest.mark.asyncio(scope="session")
async def test_set_pins(device_cluster: DeviceCluster, device_id: str):
    await device_cluster.set_pins(
        device_id,
        [
            {
                "pin": PinID.RELAY_1,
                "state": PinState.HIGH,
            },
            {
                "pin": PinID.RELAY_2,
                "state": PinState.LOW,
                "time": 500,
            },
        ],
    )


@pytest.mark.asyncio(scope="session")
async def test_set_phones(device_cluster: DeviceCluster, device_id: str):
    await device_cluster.set_phones(
        device_id,
        ["38099999999", "380911111111"],
    )


@pytest.mark.asyncio(scope="session")
async def test_update_pins(device_cluster: DeviceCluster, device_id: str):
    async def update_pins_answer(message: Message):
        payload = message.payload.json()
        answer_payload = {
            "pins": [
                {
                    "pin": pin_id,
                    "mode": PinMode.INPUT,
                    "state": PinState.HIGH,
                    "voice_call_state": VoiceCallState.HIGH,
                }
                for pin_id in payload
            ],
        }
        print("Sending update_pins answer")
        await message.fastmqtt.publish(
            f"device/{device_id}/update",
            json.dumps(answer_payload),
        )

    subscription = device_cluster._fastmqtt.register(
        update_pins_answer, f"device/{device_id}/pin/get"
    )
    await device_cluster._fastmqtt._sub_manager.subscribe(subscription)

    async with asyncio.timeout(5):
        update = await device_cluster.update_pins(
            device_id,
            [PinID.INPUT_1, PinID.OUTPUT_1],
        ).wait_responce()
        print(update)
