from typing import NotRequired, TypedDict

from .methods_base import ResponceDeviceMethod, DeviceMethod
from .types import CallbackFilter, Pin, UpdatePin, PinState


class SetPinPayload(TypedDict):
    pin: Pin
    state: PinState
    time: NotRequired[int]  # in milliseconds


class SetPinsMethod(ResponceDeviceMethod[list[UpdatePin]]):
    payload: list[SetPinPayload]
    __topic__: str = "device/{device_id}/pin/set"

    @property
    def callback_filters(self) -> list[CallbackFilter]:
        return [
            CallbackFilter(
                pin=pin["pin"],
                state=pin["state"] if "time" not in pin else ~pin["state"],
            )
            for pin in self.payload
        ]


class SetPhonesMethodPayload(TypedDict):
    phone_list: list[str]


class SetPhonesMethod(DeviceMethod):
    payload: SetPhonesMethodPayload
    __topic__: str = "device/{device_id}/phone/set"


class UpdatePinsMethod(ResponceDeviceMethod[list[UpdatePin]]):
    payload: list[Pin]
    __topic__: str = "device/{device_id}/pin/get"

    @property
    def callback_filters(self) -> list[CallbackFilter]:
        return [CallbackFilter(pin=pin) for pin in self.payload]
