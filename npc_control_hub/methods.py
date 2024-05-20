import sys

if sys.version_info >= (3, 12):
    from typing import NotRequired, TypedDict
else:
    from typing_extensions import NotRequired, TypedDict

from .methods_base import DeviceMethod, ResponceDeviceMethod
from .types import CallbackFilter, PinID, PinState, UpdatePin


class SetPinPayload(TypedDict):
    pin: PinID
    state: PinState
    time: NotRequired[int]  # in milliseconds


class SetPinsMethod(ResponceDeviceMethod[list[UpdatePin]]):
    payload: list[SetPinPayload]
    __topic__: str = "device/{device_id}/pin/set"

    @property
    def callback_filters(self) -> list[CallbackFilter]:
        return [
            CallbackFilter(
                id=pin["pin"],
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
    payload: list[PinID]
    __topic__: str = "device/{device_id}/pin/get"

    @property
    def callback_filters(self) -> list[CallbackFilter]:
        return [CallbackFilter(id=pin) for pin in self.payload]
