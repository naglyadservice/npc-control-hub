import enum

from pydantic import BaseModel


class RelayPinID(enum.StrEnum):
    RELAY_1 = "RELAY_1"
    RELAY_2 = "RELAY_2"


class OutputPinID(enum.StrEnum):
    OUTPUT_1 = "OUTPUT_1"
    OUTPUT_2 = "OUTPUT_2"


class InputPinID(enum.StrEnum):
    INPUT_1 = "INPUT_1"
    INPUT_2 = "INPUT_2"


WriteablePinID = RelayPinID | OutputPinID
ReadablePinID = InputPinID


class PinID(RelayPinID, OutputPinID, InputPinID):
    pass


class PinMode(enum.IntEnum):
    INPUT = 1
    OUTPUT = 3
    INPUT_PULLUP = 5
    INPUT_PULLDOWN = 9
    DISABLED = -1


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

        if self.pin is not None and value.pin != self.pin:
            return False

        if self.mode is not None and value.mode != self.mode:
            return False

        if self.state is not None and value.state != self.state:
            return False

        return True


class UpdatePin(BaseModel):
    id: PinID
    mode: PinMode
    state: PinState
    voice_call_state: VoiceCallState


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
