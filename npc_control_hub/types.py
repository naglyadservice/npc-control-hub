import enum

from pydantic import BaseModel, Field


class PinID(enum.StrEnum):
    RELAY_1 = "RELAY_1"
    RELAY_2 = "RELAY_2"
    OUTPUT_1 = "OUTPUT_1"
    OUTPUT_2 = "OUTPUT_2"
    INPUT_1 = "INPUT_1"
    INPUT_2 = "INPUT_2"


class PinMode(enum.IntEnum):
    INPUT = 0x01
    OUTPUT = 0x03
    PULLUP = 0x04
    INPUT_PULLUP = 0x05
    PULLDOWN = 0x08
    INPUT_PULLDOWN = 0x09
    OPEN_DRAIN = 0x10
    OUTPUT_OPEN_DRAIN = 0x13
    ANALOG = 0xC0


class PinState(enum.IntEnum):
    LOW = 0
    HIGH = 1

    def __invert__(self) -> "PinState":
        return PinState.HIGH if self == PinState.LOW else PinState.LOW


class VoiceCallState(enum.IntEnum):
    LOW = 0
    HIGH = 1
    DISABLED = -1


class CallbackFilter(BaseModel):
    id: PinID | None = None
    mode: PinMode | None = None
    state: PinState | None = None

    def __call__(self, value: "UpdatePin | CallbackFilter") -> bool:
        if not isinstance(value, (UpdatePin, CallbackFilter)):
            raise TypeError(
                f"__value must be UpdatePin or CallbackFilter, not {type(value)}"
            )

        if self.id is not None and value.id != self.id:
            return False

        if self.mode is not None and value.mode != self.mode:
            return False

        if self.state is not None and value.state != self.state:
            return False

        return True


class UpdatePin(BaseModel):
    id: PinID = Field(alias="pin")
    mode: PinMode
    state: PinState

    model_config = {"extra": "ignore"}


class UpdateCall(BaseModel):
    phone_num: str
    valid: bool


class RawUpdate(BaseModel):
    pins: list[UpdatePin] | None = None
    call: UpdateCall | None = None
    temperature_on_board: float | None = None
    temperature_outdoor: float | None = None


class Cache(BaseModel):
    pins: dict[PinID, UpdatePin] = {}
    temperature_on_board: float | None = None
    temperature_outdoor: float | None = None
