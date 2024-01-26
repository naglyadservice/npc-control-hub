from dataclasses import dataclass
from typing import Any, Literal, NotRequired, TypedDict


class Constants:
    def __init__(self) -> None:
        raise NotImplementedError("This class is not supposed to be instantiated")

    def __setattr__(self, __name: str, __value: Any) -> None:
        raise TypeError(f"Cannot set attribute {__name} of {type(self)}")


class ANY(Constants):
    pass


class PinMode(Constants):
    INPUT = 1
    OUTPUT = 3
    INPUT_PULLUP = 5
    INPUT_PULLDOWN = 9
    PIN_DISABLED = -1


class PinState(Constants):
    LOW = 0
    HIGH = 1


PinModeType = Literal[-1, 1, 3, 5, 9]
PinStateType = Literal[0, 1]
VoiceCallStateType = Literal[-1, 0, 1]


class SetPin(TypedDict):
    pin: int
    state: PinStateType
    time: NotRequired[int]  # in milliseconds


class ConfigPin(TypedDict):
    pin: int
    mode: PinModeType
    state: NotRequired[PinStateType]
    voice_call_state: NotRequired[VoiceCallStateType]


@dataclass(frozen=True)
class PinCache:
    device_id: str
    pin: int
    mode: PinModeType
    state: PinStateType
    voice_call_state: VoiceCallStateType


@dataclass(frozen=True)
class CbFilter:
    device_id: str
    pin: int | type[ANY] = ANY
    mode: PinModeType | type[ANY] = ANY
    state: PinStateType | type[ANY] = ANY

    def __eq__(self, __value: "PinCache | CbFilter") -> bool:
        if not isinstance(__value, (PinCache, CbFilter)):
            raise TypeError(f"__value must be PinCache or CbFilter, not {type(__value)}")

        if self.device_id != __value.device_id:
            return False

        if self.pin is not ANY and self.pin != __value.pin:
            return False

        if self.mode is not ANY and self.mode != __value.mode:
            return False

        if self.state is not ANY and self.state != __value.state:
            return False

        return True
